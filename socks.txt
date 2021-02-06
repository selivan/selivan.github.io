#!/bin/bash
# Homepage: selivan.github.io/socks
# Author: Pavel Selivanov
# Contributors: Vlad Safronov (Oracle Linux 7.5, Centos 7)

function get_external_address() {
	local addr=$( timeout 3 dig +short myip.opendns.com @resolver1.opendns.com || \
	timeout 3 curl -s http://ipecho.net/plain || \
	timeout 3 curl -s http://ident.me/ || \
	timeout 3 curl -s http://whatismyip.akamai.com/ )
	[ $? -ne 0 ] && addr="<this server IP address>"
	echo "$addr"
}

# args: file user password
function generate_password_file() {
	# -1    generate md5-based password hash
	echo "$2:$( openssl passwd -1 "$3" )" > "$1"
}

# args: file; generates: file.db
function generate_password_dbfile() {
	awk -F: '{print $1; print $2}' < "$1" | db_load -T -t hash "${1}.db"
}

# args: file pwdfile
function generate_pam() {
# nodelay: don't cause a delay on auth failure. Anti-DDOS
cat > "$1" << EOF
auth required pam_pwdfile.so nodelay pwdfile=$2
account required pam_permit.so
EOF
}

# args: file pwdfile
function generate_pam_userdb() {
# Note that the path to the database file should be specified without the .db suffix
cat > "$1" << EOF
auth required pam_userdb.so db=$2 crypt=crypt
account required pam_permit.so
EOF
}

# args: file interface port
function generate_config_v11() {
cat > "$1" << EOF
internal: $2 port=$3
external: $2

method: pam

user.privileged: root
user.notprivileged: nobody

client pass {
        from: 0.0.0.0/0 to: 0.0.0.0/0
        log: error
}

# deny proxied to loopback
block {
    from: 0.0.0.0/0 to: 127.0.0.0/8
    log: error
}

pass {
        from: 0.0.0.0/0 to: 0.0.0.0/0
        log: error
}
EOF
}

# args: file interface port
function generate_config_v14() {
cat > "$1" <<EOF
# https://www.inet.no/dante/doc/1.4.x/config/ipv6.html
internal.protocol: ipv4 ipv6
internal: $2 port=$3
external.protocol: ipv4 ipv6
external: $2

socksmethod: pam.any

user.privileged: root
user.notprivileged: nobody

client pass {
        from: 0.0.0.0/0 to: 0.0.0.0/0
        log: error
}

client pass {
        from: ::/0 to: ::/0
        log: error
}

# deny proxied to loopback
socks block {
    from: 0.0.0.0/0 to: 127.0.0.0/8
    log: error
}

socks block {
    from: ::/0 to: ::1/128
    log: error
}

socks pass {
        from: 0.0.0.0/0 to: 0.0.0.0/0
        log: error
}
EOF
}

# args: file interface port
function generate_systemd_file() {
cat > "$1" <<EOF
# /etc/systemd/system/sockd.service
[Unit]
Description=Dante Socks5 Daemon
After=network.target

[Service]
Type=forking
PIDFile=/var/run/sockd.pid
ExecStart=/usr/sbin/sockd -D -f /etc/sockd.conf
ExecReload=/bin/kill -HUP \${MAINPID}
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target
Alias=danted.service
EOF
}

# args: port
function open_ufw_port() {
	# Open port in firewall if required
	if which ufw > /dev/null; then
	        ufw allow "$PORT"/tcp
	fi
}

# args: port
function open_firewalld_port() {
	# Open port in firewall if required
	if which firewall-cmd > /dev/null; then
		firewall-cmd --zone=public --permanent --add-port="$1"/tcp
		firewall-cmd --reload
	fi
}

IFACE=$(ip route get 8.8.8.8 | head -1 | cut -d' ' -f5)

[ -z "$USER" ] && export USER=user
[ -z "$PORT" ] && export PORT=8080
[ -z "$PASSWORD" ] && export PASSWORD=$( cat /dev/urandom | tr --delete --complement 'a-z0-9' | head --bytes=10 )

[ -e /etc/lsb-release ] && source /etc/lsb-release
[ -e /etc/os-release ] && source /etc/os-release

# Ubuntu 16.06 Xenial
if [ "$DISTRIB_ID $DISTRIB_CODENAME" = "Ubuntu xenial" ]; then

	apt update
	apt install -y dante-server libpam-pwdfile openssl

	generate_password_file /etc/danted.passwd "$USER" "$PASSWORD"

	generate_pam /etc/pam.d/sockd /etc/danted.passwd

	generate_config_v11 /etc/danted.conf "$IFACE" "$PORT"

	open_ufw_port "$PORT"

	systemctl restart danted.service

	echo "Your socks proxy configuration:"
	echo "Address: $( get_external_address )"
	echo "Port: $PORT"
	echo "User: $USER"
	echo "Password: $PASSWORD"

# Ubuntu 18.04 Bionic
elif [ "$DISTRIB_ID $DISTRIB_CODENAME" = "Ubuntu bionic" ]; then

	apt update
	apt install -y dante-server libpam-pwdfile openssl

	generate_password_file /etc/danted.passwd "$USER" "$PASSWORD"

	generate_pam /etc/pam.d/sockd /etc/danted.passwd

	generate_config_v14 /etc/danted.conf "$IFACE" "$PORT"

	open_ufw_port "$PORT"

	systemctl restart danted.service

	echo "Your socks proxy configuration:"
	echo "Address: $( get_external_address )"
	echo "Port: $PORT"
	echo "User: $USER"
	echo "Password: $PASSWORD"

# Ubuntu 20.04 Focal
elif [ "$ID $VERSION_CODENAME" = "ubuntu focal" ]; then

	apt update
	apt install -y dante-server libpam-pwdfile openssl

	generate_password_file /etc/danted.passwd "$USER" "$PASSWORD"

	generate_pam /etc/pam.d/sockd /etc/danted.passwd

	generate_config_v14 /etc/danted.conf "$IFACE" "$PORT"

	open_ufw_port "$PORT"

	systemctl restart danted.service

	echo "Your socks proxy configuration:"
	echo "Address: $( get_external_address )"
	echo "Port: $PORT"
	echo "User: $USER"
	echo "Password: $PASSWORD"

# CentOS 7 and Oracle Linux 7.5
elif [ "$ID $VERSION_ID" = "ol 7.5" -o "$ID $VERSION_ID" = "centos 7" ]; then

	DANTE_TGZ="tgz-prod.dante-1.4.2-rhel72-amd64-64bit-gcc.tar.gz"
	curl --progress-bar -O https://www.inet.no/dante/sslfiles/dante-1.4.2/"$DANTE_TGZ"
	tar -C / -xzf "$DANTE_TGZ"

	yum install -q -y openssl which bind-utils

	generate_password_file /etc/danted.passwd "$USER" "$PASSWORD"

	generate_password_dbfile /etc/danted.passwd

	generate_pam_userdb /etc/pam.d/sockd /etc/danted.passwd

	generate_config_v14 /etc/sockd.conf "$IFACE" "$PORT"

	open_firewalld_port "$PORT"

	generate_systemd_file /etc/systemd/system/sockd.service

	systemctl daemon-reload

	systemctl enable sockd.service

	systemctl restart sockd.service

	echo "Your socks proxy configuration:"
	echo "Address: $( get_external_address )"
	echo "Port: $PORT"
	echo "User: $USER"
	echo "Password: $PASSWORD"

else

	echo "Sorry, this distribution is not supported"
	echo "Feel free to send patches to selivan.github.io/socks to add support for more"
	echo "Supported distributions:"
	echo "- Ubuntu 16.04 Xenial"
	echo "- Ubuntu 18.04 Bionic"
	echo "- Ubuntu 20.04 Focal"
	echo "- Oracle Linux 7.5"
	echo "- Centos 7"
	exit 1

fi
