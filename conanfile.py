from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conanos.build import config_scheme
import os, shutil

class LibsrtpConan(ConanFile):
    name = "libsrtp"
    version = "2.2.0"
    description = "Library for SRTP (Secure Realtime Transport Protocol)"
    url = "https://github.com/conanos/libsrtp"
    homepage = "https://github.com/cisco/libsrtp"
    license = "BSD"
    exports = ["LICENSE"]
    generators = "visual_studio", "gcc"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = { 'shared': True, 'fPIC': True }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def source(self):
        url_="https://github.com/cisco/libsrtp/archive/v{version}.tar.gz"
        tools.get(url_.format(version=self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
    
    def build(self):
        if self.settings.os == 'Windows':
            with tools.chdir(os.path.join(self._source_subfolder)):
                msbuild = MSBuild(self)
                build_type = str(self.settings.build_type) + (" Dll" if self.options.shared else "")
                msbuild.build("srtp.sln",upgrade_project=True,platforms={'x86': 'Win32', 'x86_64': 'x64'}, build_type=build_type)
        
        #with tools.chdir(self.source_subfolder):
        #    _args = ["--prefix=%s/builddir"%(os.getcwd())]
        #    
        #    autotools = AutoToolsBuildEnvironment(self)
        #    autotools.configure(args=_args)
        #    autotools.make(args=["-j4"],make_program='make all shared_library')
        #    autotools.install()

    def package(self):
        if self.settings.os == 'Windows':
            build_type = str(self.settings.build_type) + (" Dll" if self.options.shared else "")
            platforms = {'x86': 'Win32', 'x86_64': 'x64'}
            output_rpath = os.path.join(platforms.get(str(self.settings.arch)),build_type)
            self.copy("srtp2.*", dst=os.path.join(self.package_folder,"lib"),
                      src=os.path.join(self.build_folder,self._source_subfolder,output_rpath), excludes=["srtp2.dll","srtp2.tlog"])
            self.copy("srtp2.dll", dst=os.path.join(self.package_folder,"bin"),
                      src=os.path.join(self.build_folder,self._source_subfolder,output_rpath))
            self.copy("srtp.h", dst=os.path.join(self.package_folder,"include","srtp2"),
                      src=os.path.join(self.build_folder,self._source_subfolder,"include"))

            tools.mkdir(os.path.join(self.package_folder,"lib","pkgconfig"))
            shutil.copyfile(os.path.join(self.build_folder,self._source_subfolder,"libsrtp2.pc.in"),
                            os.path.join(self.package_folder,"lib","pkgconfig", "libsrtp2.pc"))
            replacements = {
                "@prefix@"          : self.package_folder,
                "@libdir@"          : "${prefix}/lib",
                "@includedir@"      : "${prefix}/include",
                "@PACKAGE_NAME@"    : self.name,
                "@PACKAGE_VERSION@" : self.version,
                "@LIBS@"            : ""
            }
            for s, r in replacements.items():
                tools.replace_in_file(os.path.join(self.package_folder,"lib","pkgconfig", "libsrtp2.pc"),s,r)

        #if tools.os_info.is_linux:
        #    with tools.chdir(self.source_subfolder):
        #        if self.options.shared:
        #            excludes="*.a"
        #        else:
        #            excludes="*.so*"
        #        self.copy("*", src="%s/builddir"%(os.getcwd()), excludes=excludes)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

