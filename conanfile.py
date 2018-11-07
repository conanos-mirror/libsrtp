from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
from shutil import copyfile
import os

class LibsrtpConan(ConanFile):
    name = "libsrtp"
    version = "1.6.0"
    description = "Library for SRTP (Secure Realtime Transport Protocol)"
    url = "https://github.com/conan-multimedia/libsrtp"
    homepage = "https://github.com/cisco/libsrtp"
    license = "BSD_like"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    source_subfolder = "source_subfolder"

    def source(self):
        tools.get("http://172.16.64.65:8081/artifactory/gstreamer/{name}-{version}.tar.gz".format(name=self.name,version=self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):

        #self.run('./configure --prefix %s/build --libdir %s/build/lib --disable-maintainer-mode'
        #' --disable-silent-rules  --enable-introspection'%(os.getcwd(),os.getcwd()))
        #self.run('make -j4 all shared_library')
        #self.run('make install')
        
        with tools.chdir(self.source_subfolder):
            _args = ["--prefix=%s/builddir"%(os.getcwd())]

            #if self.options.shared:
            #    _args.extend(['--enable-shared=yes','--enable-static=no'])
            #else:
            #    _args.extend(['--enable-shared=no','--enable-static=yes'])

            #self.run('./configure %s'%(' '.join(_args)))
            #self.run('make -j4')
            #self.run('make install')
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=_args)
            autotools.make(args=["-j4"],make_program='make all shared_library')
            autotools.install()

    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                if self.options.shared:
                    excludes="*.a"
                else:
                    excludes="*.so*"
                self.copy("*", src="%s/builddir"%(os.getcwd()), excludes=excludes)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

