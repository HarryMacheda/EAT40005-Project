#include <iostream>
#include <vector>
#include <cmath>
#include <csignal>
#include <unistd.h>

#include "sl_lidar.h" 
#include "sl_lidar_driver.h"
#include "matplotlibcpp.h"

namespace plt = matplotlibcpp;
using namespace sl;

bool ctrl_c_pressed = false;
void ctrlc(int) {
    ctrl_c_pressed = true;
}

#ifndef _countof
#define _countof(arr) (sizeof(arr) / sizeof(arr[0]))
#endif

bool checkSLAMTECLIDARHealth(ILidarDriver* drv) {
    sl_lidar_response_device_health_t healthinfo;
    sl_result op_result = drv->getHealth(healthinfo);
    if (SL_IS_OK(op_result)) {
        if (healthinfo.status == SL_LIDAR_STATUS_ERROR) {
            std::cerr << "Lidar internal error. Please reboot." << std::endl;
            return false;
        }
        return true;
    } else {
        std::cerr << "Cannot retrieve Lidar health info." << std::endl;
        return false;
    }
}

int main(int argc, const char * argv[]) {
    const char * port = "/dev/ttyUSB0"; // change to your port
    sl_u32 baudrate = 460800;

    IChannel* _channel = *createSerialPortChannel(port, baudrate);
    ILidarDriver* drv = *createLidarDriver();

    if (!drv || SL_IS_FAIL(drv->connect(_channel))) {
        std::cerr << "Failed to connect to LIDAR" << std::endl;
        return -1;
    }

    sl_lidar_response_device_info_t devinfo;
    if (SL_IS_FAIL(drv->getDeviceInfo(devinfo))) {
        std::cerr << "Failed to get device info" << std::endl;
        return -1;
    }

    if (!checkSLAMTECLIDARHealth(drv)) return -1;

    signal(SIGINT, ctrlc);
    drv->setMotorSpeed(); // default speed
    drv->startScan(0, 1);

    while (!ctrl_c_pressed) {
        sl_lidar_response_measurement_node_hq_t nodes[8192];
        size_t count = _countof(nodes);

        if (SL_IS_OK(drv->grabScanDataHq(nodes, count))) {
            drv->ascendScanData(nodes, count);

            std::vector<double> xs, ys;
            for (size_t i = 0; i < count; ++i) {
                float angle = (nodes[i].angle_z_q14 * 90.0f) / 16384.0f;
                float dist = nodes[i].dist_mm_q2 / 1000.0f / 4.0f; // meters
                if (dist > 0.1 && dist < 6.0) { // filter some noise
                    double rad = angle * M_PI / 180.0;
                    xs.push_back(dist * cos(rad));
                    ys.push_back(dist * sin(rad));
                }
            }

            plt::clf();
            plt::xlim(-6, 6);
            plt::ylim(-6, 6);
            plt::plot(xs, ys, "r.");
            plt::title("Real-Time LIDAR Scan");
            plt::pause(0.001);
        }
    }

    std::cout << "Stopping..." << std::endl;
    drv->stop();
    drv->setMotorSpeed(0);
    delete drv;
    return 0;
}
