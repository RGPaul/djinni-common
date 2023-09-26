from conan import ConanFile
from conan.errors import ConanException
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import to_apple_arch
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import save, load, copy, collect_libs
from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps
import os

class DjinniCommonConan(ConanFile):
    name = "djinni-common"
    version = "1.0.4"
    author = "Ralph-Gordon Paul (development@rgpaul.com)"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "android_ndk": [None, "ANY"], 
        "android_stl_type":["c++_static", "c++_shared"]}
    default_options = {"shared": False, "android_ndk": None, "android_stl_type": "c++_static"}
    description = "This library contains functions that are commonly used in djinni projects."
    url = "https://github.com/RGPaul/djinni-common"
    license = "MIT"
    exports_sources = "cmake-modules/*", "src/*", "CMakeLists.txt", "djinni/*", "run-djinni.sh"
    generators = "CMakeDeps"

    def generate(self):
        djinni_dep = self.dependencies["djinni"]
        copy(self, "djinni.jar", os.path.join(djinni_dep.package_folder, "bin"), os.path.join(self.build_folder, "bin"))
        
        tc = CMakeToolchain(self)

        self.run(os.path.join(self.build_folder, "run-djinni.sh"))

        if self.settings.os == "Android":
            self.applyCmakeSettingsForAndroid(tc)

        if self.settings.os == "iOS":
            self.applyCmakeSettingsForiOS(tc)

        if self.settings.os == "Macos":
            self.applyCmakeSettingsFormacOS(tc)

        # build static library if shared option is disabled
        tc.variables["BUILD_STATIC_LIB"] = "OFF" if self.options.shared else "ON"

        tc.generate()

    # compile using cmake
    def build(self):
        cmake = CMake(self)
        cmake.verbose = True
        cmake.configure()
        cmake.build()
        cmake.install()

    def applyCmakeSettingsForAndroid(self, tc):
        android_toolchain = os.environ["ANDROID_NDK_PATH"] + "/build/cmake/android.toolchain.cmake"
        tc.variables["CMAKE_TOOLCHAIN_FILE"] = android_toolchain
        tc.variables["ANDROID_NDK"] = os.environ["ANDROID_NDK_PATH"]
        tc.variables["ANDROID_STL"] = self.options.android_stl_type
        tc.variables["ANDROID_NATIVE_API_LEVEL"] = self.settings.os.api_level
        tc.variables["ANDROID_TOOLCHAIN"] = "clang"
        tc.variables["DJINNI_WITH_JNI"] = True

    def applyCmakeSettingsForiOS(self, tc):
        tc.cache_variables["CMAKE_SYSTEM_NAME"] = "iOS"
        tc.cache_variables["CMAKE_OSX_DEPLOYMENT_TARGET"] = "10.0"
        tc.cache_variables["DJINNI_WITH_OBJC"] = True
        tc.cache_variables["CMAKE_OSX_SYSROOT"] = "/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk"
        tc.cache_variables["CMAKE_OSX_ARCHITECTURES"] = "armv7;armv7s;arm64;arm64e"

        # define all architectures for ios fat library
        if "arm" in self.settings.arch:
            tc.cache_variables["CMAKE_OSX_ARCHITECTURES"] = "armv7;armv7s;arm64;arm64e"
        else:
            tc.cache_variables["CMAKE_OSX_ARCHITECTURES"] = to_apple_arch(self)
        

    def applyCmakeSettingsFormacOS(self, tc):
        tc.cache_variables["CMAKE_OSX_ARCHITECTURES"] = to_apple_arch(self)
        tc.cache_variables["DJINNI_WITH_OBJC"] = True
        
    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.includedirs = ['include']

    def package_id(self):
        if "arm" in self.info.settings.get_safe("arch") and self.info.settings.get_safe("os") == "iOS":
            self.info.settings.arch = "AnyARM"

    def requirements(self):
        self.requires("boost/1.82.0")
        self.requires("djinni/470@%s/%s" % (self.user, self.channel))
        self.requires("nlohmann_json/3.11.2")

    def configure(self):
        if self.settings.os == "Android":
            self.options["boost"].shared = False
            self.options["boost"].android_ndk = self.options.android_ndk
            self.options["boost"].android_stl_type = self.options.android_stl_type
            self.options["boost"].without_context = True
            self.options["boost"].without_coroutine = True
            self.options["boost"].without_fiber = True
            self.options["boost"].without_locale = True
            self.options["boost"].without_python = True
            self.options["boost"].without_stacktrace = True
            self.options["boost"].with_stacktrace_backtrace = False

            self.options["djinni"].shared = self.options.shared
            self.options["djinni"].android_ndk = self.options.android_ndk
            self.options["djinni"].android_stl_type = self.options.android_stl_type

    def config_options(self):
        # remove android specific option for all other platforms
        if self.settings.os != "Android":
            del self.options.android_ndk
            del self.options.android_stl_type
