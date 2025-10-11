/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2024-2025. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <iostream>
#include <cstdio>
#include <fstream>
#include "AscendIE.h"

using namespace AscendIE;

int main(int argc, char** argv)
{
    const int inputIndex = 4;
    if (argc != inputIndex) {
        std::cout << "For AIE model convert, only three parameters: model, output and soc_version are needed."
            << std::endl;
        return -1;
    }
    std::string onnxModelPath = argv[1];
    std::string outputPath = argv[2];
    std::string socVersion = argv[3];

    Builder* builder = Builder::CreateInferBuilder(socVersion.c_str());

    auto network = builder->CreateNetwork();

    std::string moddelPath(onnxModelPath);

    OnnxModelParser parser;

    bool ret = parser.Parse(network, onnxModelPath.c_str());

    BuilderConfig config;

    config.SetFlag(BuilderFlag::FP16);

    auto modelData = builder->BuildModel(network, config);

    std::ofstream fout(outputPath, std::ios::binary);
    // 检查打开文件是否成功
    if (!fout) {
        throw std::runtime_error("Failed to open: " + outputPath);
    }

    fout.write((char*)modelData.data.get(), modelData.size);
    // 检查写入是否成功，否则清除残留文件
    if (!fout) {
        fout.close();
        remove(outputPath.c_str());
        throw std::runtime_error("Failed to write to: " + outputPath);
    }

    fout.close();
    // 检查关闭文件是否成功
    if (!fout) {
        remove(outputPath.c_str());
        throw std::runtime_error("Failed to close file: " + outputPath);
    }

    std::cout << "AIE Model Convert Succeed" << std::endl;

    delete builder;

    Finalize();
}
