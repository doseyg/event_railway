Use Ubuntu 19.10


apt-get update 
apt-get install -y --no-install-recommends curl ca-certificates gnupg2
echo 'deb http://download.opensuse.org/repositories/security:/zeek/xUbuntu_19.10/ /' > /etc/apt/sources.list.d/security:zeek.list
curl https://download.opensuse.org/repositories/security:/zeek/xUbuntu_19.10/Release.key | apt-key add -
apt-get update
apt-get install -y --no-install-recommends zeek-lts zeek-lts-core-dev
apt-get install -y --no-install-recommends git ninja-build ccache g++ llvm-9-dev clang-9 libclang-9-dev bison flex libfl-dev python3 python3-pip zlib1g-dev jq locales-all python3-setuptools python3-wheel
pip3 install btest pre-commit
apt-get install -y --no-install-recommends python3-sphinx python3-sphinx-rtd-them
apt-get install -y --no-install-recommends python3-sphinx python3-sphinx-rtd-theme
apt-get clean
mkdir /usr/local/cmake
cd /usr/local/cmake/
curl -L https://github.com/Kitware/CMake/releases/download/v3.15.0/cmake-3.15.0-Linux-x86_64.tar.gz | tar xzvf - -C /usr/local/cmake --strip-components 1
export PATH="/usr/local/cmake/bin:${PATH}"
cd /root/
#wget https://api.cirrus-ci.com/v1/artifact/github/zeek/spicy/docker_ubuntu_19_10/packages/build/spicy-linux.tar.gz
#tar xvf spicy-linux.tar.gz -C /opt/spicy --strip-components=1
mkdir /opt/spicy/src
cd /opt/spicy/src
git clone https://github.com/zeek/spicy.git
cd /opt/spicy/src && git submodule update --recursive --init
./configure --generator=Ninja --prefix=/opt/spicy --with-zeek=/opt/zeek
make



Example hexedit and test
echo 88b8000a00000000010203040506 | xxd -p -r > f
cat f | spicy-driver goose.spicy 
[$appid=35000, $length=10, $reserved1=0, $reserved2=0]



Link Spicy to Zeek
export ZEEK_PLUGIN_PATH=$(spicy-config --zeek-plugin-path)
