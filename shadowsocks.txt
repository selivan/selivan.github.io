#!/bin/bash
# Homepage: selivan.github.io/socks
# Author: Pavel Selivanov
# Contributors: Octavian Dodita(CentOS 7, RHEL 7), Konstantin Kuchinin(Debian 8)

function get_external_address() {
	local addr=$( timeout 3 curl -s http://whatismyip.akamai.com/ || \
	timeout 3 curl -s http://ifconfig.io/ip || \
	timeout 3 curl -s http://ipecho.net/plain || \
	timeout 3 curl -s http://ident.me/
	)
	[ $? -ne 0 ] && addr="<this server IP address>"
	echo "$addr"
}

# args: file port password
function generate_config() {
# "fast_open": true reduces connection latency. But it doesn't work on OpenVZ, on old kernels, and on kernels where this feature is disabled
cat > "$1" <<EOF
{
    "server":"0.0.0.0",
    "server_port":$2,
    "local_port":1080,
    "password":"$3",
    "timeout":60,
    "method":"chacha20-ietf-poly1305"
}
EOF
}

# args: method password
function generate_hash() {
	echo -n "$1":"$2" | base64
}

# args: port
function open_ufw_port() {
	# Open port in firewall if required
	if type ufw > /dev/null; then
	        ufw allow "$PORT"/tcp
	fi
}

# args: port
function open_firewalld_port() {
	# Open port in firewall if required
	if type firewall-cmd > /dev/null; then
		firewall-cmd --zone=public --permanent --add-port="$1"/tcp
		firewall-cmd --reload
	fi
}

# args: password port
function print_config() {
	echo
	echo "Your shadowsocks proxy configuration:"
	echo "URL: ss://$( generate_hash chacha20-ietf-poly1305 $1 )@$( get_external_address ):$2"
	echo "Android client: https://play.google.com/store/apps/details?id=com.github.shadowsocks"
	echo "Clients for other devices: https://shadowsocks.org/en/download/clients.html"
}

IFACE=$(ip route get 8.8.8.8 | head -1 | cut -d' ' -f5)
USER=user

[ -z "$PORT" ] && export PORT=8000
[ -z "$PASSWORD" ] && export PASSWORD=$( cat /dev/urandom | tr --delete --complement 'a-z0-9' | head --bytes=12 )

[ -e /etc/lsb-release ] && source /etc/lsb-release
[ -e /etc/os-release ] && source /etc/os-release

[ -e /etc/debian_version ] && export DISTRIB_ID=Debian && export DISTRIB_CODENAME=$(dpkg --status tzdata|grep Provides|cut -f2 -d'-')

# Ubuntu 16.06 Xenial
if [ "$DISTRIB_ID $DISTRIB_CODENAME" = "Ubuntu xenial" ]; then

	apt update
	apt install -y software-properties-common
	apt-add-repository -y ppa:max-c-lv/shadowsocks-libev
	apt update
	apt install -y shadowsocks-libev

	# package does not create config directory :(
	mkdir -p /etc/shadowsocks-libev
	generate_config /etc/shadowsocks-libev/config.json "$PORT" "$PASSWORD"

	open_ufw_port "$PORT"

	systemctl enable shadowsocks-libev
	systemctl restart shadowsocks-libev

	print_config "$PASSWORD" "$PORT"

# Ubuntu 18.04 Bionic
elif [ "$DISTRIB_ID $DISTRIB_CODENAME" = "Ubuntu bionic" ]; then

	apt update
	apt install -y shadowsocks-libev

	# package does not create config directory :(
	mkdir -p /etc/shadowsocks-libev
	generate_config /etc/shadowsocks-libev/config.json "$PORT" "$PASSWORD"

	open_ufw_port "$PORT"

	systemctl enable shadowsocks-libev
	systemctl restart shadowsocks-libev

	print_config "$PASSWORD" "$PORT"

# CentOS 7 and RHEL 7
# Example of /etc/os-release for RHEL: https://linuxconfig.org/how-to-check-redhat-version#h5-5-check-release-files
elif [[ "$ID $VERSION_ID" == "centos 7"* || "$ID $VERSION_ID" == "rhel 7"* ]]; then

	yum install -y epel-release
	curl --location --output "/etc/yum.repos.d/librehat-shadowsocks-epel-7.repo" "https://copr.fedorainfracloud.org/coprs/librehat/shadowsocks/repo/epel-7/librehat-shadowsocks-epel-7.repo"
	# Sometimes cache is not completely updated after adding new repo
	yum makecache
	yum install -y bind-utils mbedtls
	ln -sf /usr/lib64/libmbedcrypto.so.1 /usr/lib64/libmbedcrypto.so.0
	yum install -y shadowsocks-libev

	generate_config /etc/shadowsocks-libev/config.json "$PORT" "$PASSWORD"

	systemctl daemon-reload
	systemctl enable shadowsocks-libev
	systemctl restart shadowsocks-libev

	print_config "$PASSWORD" "$PORT"
	
# Debian 8
elif [ "$DISTRIB_ID $DISTRIB_CODENAME" = "Debian jessie" ]; then

	echo "deb http://archive.debian.org/debian jessie-backports main" | tee -a /etc/apt/sources.list
	echo "deb http://archive.debian.org/debian jessie-backports-sloppy main" | tee -a /etc/apt/sources.list
	echo "Acquire::Check-Valid-Until \"false\";" | tee -a /etc/apt/apt.conf.d/99DISABLE-check
	apt-get update
	aptitude -t jessie-backports-sloppy install --add-user-tag shadowsocks -y shadowsocks-libev

	# package does not create config directory :(
	mkdir -p /etc/shadowsocks-libev
	generate_config /etc/shadowsocks-libev/config.json "$PORT" "$PASSWORD"

	ufw allow "$PORT"/tcp
	ufw allow "$PORT"/udp

	systemctl enable shadowsocks-libev
	systemctl restart shadowsocks-libev

	print_config "$PASSWORD" "$PORT"

else

	echo "Sorry, this distribution is not supported"
	echo "Feel free to send patches to selivan.github.io/socks to add support for more"
	echo "Supported distributions:"
	echo "- Ubuntu 16.04 Xenial"
	echo "- Ubuntu 18.04 Bionic"
	echo "- CentOS 7"
	echo "- RHEL 7"
	echo "- Debian 8"
	exit 1

fi
