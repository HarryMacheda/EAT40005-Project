#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <nlohmann/json.h>  // For JSON serialization, you can use a library like jsoncpp

#include "sl_lidar.h" 
#include "sl_lidar_driver.h"

#define SERVER_PORT 8080
#define SERVER_IP "127.0.0.1"  // You can change this to the target IP

using namespace sl;

// Signal handler for Ctrl+C
volatile sig_atomic_t ctrl_c_pressed = 0;

void handle_sigint(int sig) {
    ctrl_c_pressed = 1;
}

// Function to send LIDAR data via TCP socket
void send_lidar_data(const std::string &data) {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("Socket creation failed");
        return;
    }

    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    server_addr.sin_addr.s_addr = inet_addr(SERVER_IP);

    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Connection failed");
        close(sockfd);
        return;
    }

    // Send data to server
    ssize_t sent_size = send(sockfd, data.c_str(), data.size(), 0);
    if (sent_size < 0) {
        perror("Send failed");
    } else {
        printf("Data sent: %s\n", data.c_str());
    }

    close(sockfd);
}

bool checkSLAMTECLIDARHealth(ILidarDriver *drv) {
    sl_result op_result;
    sl_lidar_response_device_health_t healthinfo;

    op_result = drv->getHealth(healthinfo);
    if (SL_IS_OK(op_result)) {
        printf("SLAMTEC Lidar health status : %d\n", healthinfo.status);
        if (healthinfo.status == SL_LIDAR_STATUS_ERROR) {
            fprintf(stderr, "Error, slamtec lidar internal error detected. Please reboot the device to retry.\n");
            return false;
        } else {
            return true;
        }
    } else {
        fprintf(stderr, "Error, cannot retrieve the lidar health code: %x\n", op_result);
        return false;
    }
}

int main(int argc, const char *argv[]) {
    const char *opt_is_channel = NULL;
    const char *opt_channel = NULL;
    const char *opt_channel_param_first = NULL;
    sl_u32 opt_channel_param_second = 0;
    sl_u32 baudrateArray[2] = {115200, 256000};
    sl_result op_result;
    int opt_channel_type = CHANNEL_TYPE_SERIALPORT;

    IChannel* _channel;

    printf("Ultra simple LIDAR data grabber for SLAMTEC LIDAR.\n"
           "Version: %s\n", SL_LIDAR_SDK_VERSION);

    if (argc > 1) {
        opt_is_channel = argv[1];
    } else {
        printf("Usage: %s --channel --serial <com port> [baudrate]\n", argv[0]);
        return -1;
    }

    // Create the driver instance
    ILidarDriver* drv = *createLidarDriver();
    if (!drv) {
        fprintf(stderr, "insufficient memory, exit\n");
        exit(-2);
    }

    sl_lidar_response_device_info_t devinfo;
    bool connectSuccess = false;

    // Set up the serial connection (same as the original code)...

    // Now that the connection is established...
    if (!checkSLAMTECLIDARHealth(drv)) {
        goto on_finished;
    }

    // Start the scan...
    drv->startScan(0, 1);

    // Fetch results and send them via socket
    signal(SIGINT, handle_sigint);  // Register the signal handler for Ctrl+C
    while (1) {
        sl_lidar_response_measurement_node_hq_t nodes[8192];
        size_t count = sizeof(nodes) / sizeof(nodes[0]);

        op_result = drv->grabScanDataHq(nodes, count);
        if (SL_IS_OK(op_result)) {
            drv->ascendScanData(nodes, count);

            // Create JSON object to store the LIDAR data
            Json::Value root;
            Json::Value nodeData(Json::arrayValue);
            for (int pos = 0; pos < (int)count; ++pos) {
                Json::Value node;
                node["theta"] = (nodes[pos].angle_z_q14 * 90.f) / 16384.f;
                node["distance"] = nodes[pos].dist_mm_q2 / 4.0f;
                node["quality"] = nodes[pos].quality >> SL_LIDAR_RESP_MEASUREMENT_QUALITY_SHIFT;

                nodeData.append(node);
            }
            root["data"] = nodeData;

            // Convert JSON object to string
            Json::StreamWriterBuilder writer;
            std::string dataString = Json::writeString(writer, root);

            // Send the data
            send_lidar_data(dataString);
        }

        // Handle CTRL+C exit
        if (ctrl_c_pressed) {
            break;
        }
    }

    drv->stop();
    usleep(200000);  // Sleep for 200 milliseconds

on_finished:
    if (drv) {
        delete drv;
        drv = NULL;
    }

    return 0;
}
