//    Copyright 2023 Jij Inc.

//    Licensed under the Apache License, Version 2.0 (the "License");
//    you may not use this file except in compliance with the License.
//    You may obtain a copy of the License at

//        http://www.apache.org/licenses/LICENSE-2.0

//    Unless required by applicable law or agreed to in writing, software
//    distributed under the License is distributed on an "AS IS" BASIS,
//    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//    See the License for the specific language governing permissions and
//    limitations under the License.

#pragma once

#include <openjij/utility/random.hpp>

namespace openjij {

/**
 * Note:
 *
 * By default, cxxjij (python implementation of openjij) is installed following
 * the configuration listed below. If you want to use cxxjij with non-default
 * settings (e.g. using mersenne twister, calculating with long double
 * precision, etc), please change the following configuration and recompile with
 * the command:
 *
 * $ python setup.py clean && python setup.py install
 *
 */

/**********************************************************
 default floating point precision on CPU (default: double)
 **********************************************************/
using FloatType = double;
// using FloatType = float;
// using FloatType = long double;

/**********************************************************
 default random number engine on CPU (default: xorshift)
 you may use mersenne twister or your own random number generator.
 **********************************************************/
using RandomEngine = utility::Xorshift;
// using RandomEngine = std::mt19937;
//...

} // namespace openjij
