package com.example.temidata;

import android.annotation.SuppressLint;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.robotemi.sdk.Robot;
import com.robotemi.sdk.TtsRequest;
import com.robotemi.sdk.listeners.OnRobotReadyListener;
import com.robotemi.sdk.navigation.listener.OnCurrentPositionChangedListener;
import com.robotemi.sdk.navigation.model.Position;
import com.robotemi.sdk.navigation.model.SpeedLevel;

import java.util.Locale;
import java.util.Timer;
import java.util.TimerTask;

public class MainActivity extends AppCompatActivity implements OnRobotReadyListener, OnCurrentPositionChangedListener {

    private static final String TAG = "TemiOdometryLogger";
    private static final int LOGGING_FREQUENCY_MS = 500;

    private Robot robot;
    private TextView statusText;
    private TextView odometryText;
    private Button startLoggingButton;
    private Button toggleFollowButton;

    private boolean isLogging = false;
    private boolean isFollowing = false;
    private Timer logTimer;
    private final Handler handler = new Handler(Looper.getMainLooper());

    private volatile float currentX = 0f;
    private volatile float currentY = 0f;
    private volatile float currentYaw = 0f;
    private volatile float currentTilt = 0f;

    @SuppressLint("MissingInflatedId")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        statusText = findViewById(R.id.status_text);
        odometryText = findViewById(R.id.odometry_text);
        startLoggingButton = findViewById(R.id.start_logging_button);
        toggleFollowButton = findViewById(R.id.toggle_follow_button);

        statusText.setText("Initializing Temi SDK...");
        startLoggingButton.setEnabled(false);
        toggleFollowButton.setEnabled(false);
        toggleFollowButton.setBackgroundColor(0xFF4CAF50); // Green

        robot = Robot.getInstance();
        if (robot != null) {
            robot.addOnRobotReadyListener(this);
            robot.addOnCurrentPositionChangedListener(this);
        } else {
            statusText.setText("Temi SDK initialization failed");
        }

        startLoggingButton.setOnClickListener(v -> toggleLogging());
        toggleFollowButton.setOnClickListener(v -> toggleFollowMode());
    }

    @Override
    public void onRobotReady(boolean isReady) {
        if (isReady) {
            statusText.setText("Temi Ready! Tap buttons to start.");
            startLoggingButton.setEnabled(true);
            toggleFollowButton.setEnabled(true);
            robot.speak(TtsRequest.create("Temi is ready. Press buttons to start logging or following.", false));
        } else {
            statusText.setText("Temi SDK not ready.");
            startLoggingButton.setEnabled(false);
            toggleFollowButton.setEnabled(false);
        }
    }

    private void toggleLogging() {
        if (isLogging) {
            stopLogging();
        } else {
            startLogging();
        }
    }

    private void startLogging() {
        if (isLogging) return;

        logTimer = new Timer();
        logTimer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                logCurrentPosition();
            }
        }, 0, LOGGING_FREQUENCY_MS);

        isLogging = true;
        runOnUiThread(() -> {
            startLoggingButton.setText("Stop Logging");
            statusText.setText("Logging odometry to terminal...");
            Toast.makeText(this, "Started logging", Toast.LENGTH_SHORT).show();
        });
        robot.speak(TtsRequest.create("Started logging to terminal", false));
    }

    private void stopLogging() {
        if (!isLogging) return;

        if (logTimer != null) {
            logTimer.cancel();
            logTimer = null;
        }

        isLogging = false;
        runOnUiThread(() -> {
            startLoggingButton.setText("Start Logging");
            statusText.setText("Logging stopped.");
            Toast.makeText(this, "Stopped logging", Toast.LENGTH_SHORT).show();
        });
        robot.speak(TtsRequest.create("Stopped logging", false));
    }

    private void logCurrentPosition() {
        String logData = String.format(Locale.US,
                "X=%.4f, Y=%.4f, Yaw=%.2f°, Tilt=%.2f°",
                currentX, currentY, currentYaw, currentTilt);

        Log.d(TAG, logData);
        System.out.println(logData);
    }


    private void updateOdometryDisplay(Position pos) {
        String display = String.format(Locale.US,
                "X: %.2f m\nY: %.2f m\nYaw: %.2f°\nTilt: %.2f°",
                (float) pos.getX(),
                (float) pos.getY(),
                (float) Math.toDegrees(pos.getYaw()),
                (float) Math.toDegrees(pos.getTiltAngle()));

        runOnUiThread(() -> odometryText.setText(display));
    }

    private void toggleFollowMode() {
        if (!isFollowing) {
            isFollowing = true;
            toggleFollowButton.setText("Stop Following");
            toggleFollowButton.setBackgroundColor(0xFFF44336); // Red
            statusText.setText("Temi is following...");
            robot.beWithMe(SpeedLevel.MEDIUM);
        } else {
            isFollowing = false;
            toggleFollowButton.setText("Start Following");
            toggleFollowButton.setBackgroundColor(0xFF4CAF50); // Green
            statusText.setText("Temi stopped.");
            robot.stopMovement();
        }
    }

    @Override
    public void onCurrentPositionChanged(Position position) {
        currentX = (float) position.getX();
        currentY = (float) position.getY();
        currentYaw = (float) Math.toDegrees(position.getYaw());
        currentTilt = (float) Math.toDegrees(position.getTiltAngle());

        updateOdometryDisplay(position);
    }

}