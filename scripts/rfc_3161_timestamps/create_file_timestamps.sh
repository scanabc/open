#!/bin/bash -e

# Creates timestamps from e.g. jira or confluence backups
# using a timestamp service freetsa.org.
# Copies all files from <directory_of_backups> to <target_path>,
# for each file that's not already been timestamped.
# After copying file, performs the timestamping operation using openssl ts and curl commands.
# This will result in two additional files: file.tsq.tmp and file.tsr.tmp.
# Finally, the generated signature is verified against the TSA certificate and CA
# and file extension .tmp is removed.
#
# Example commands to use this in a confluence server. We're assuming confluence is running as user "confluence1".
# 1. mkdir -p /var/backup-timestamps/confluence
# 2. chown confluence1:confluence1 /var/backup-timestamps/confluence
# 3. cd /var/backup-timestamps/confluence
# 4. curl -O https://freetsa.org/files/cacert.pem -O https://freetsa.org/files/tsa.crt
# 5. Place this script in /var/backup-timestamps/create_file_timestamps.sh
# 6. sudo -u confluence1 /var/backup-timestamps/create_file_timestamps.sh /var/atlassian/application-data/confluence/backups /var/backup-timestamps/confluence
# 7. Finally, you can do this automatically by adding the following in cron:
#    6 0 * * * sudo -u confluence1 /var/backup-timestamps/create_file_timestamps.sh /var/atlassian/application-data/confluence/backups /var/backup-timestamps/confluence

in_backups_path="$1"
target_path="$2"
if [ -z "$2" ]; then
	echo "Usage: $0 <directory_of_backups> <target_path>"
	exit 1
fi

if [ ! -d "$in_backups_path" ]; then
	echo "dir $in_backups_path does not exist"
	exit 1
fi
if [ ! -d "$target_path" ]; then
	echo "dir $target_path does not exist"
	exit 1
fi

pushd $in_backups_path/
for f in *; do
	target="$target_path/$f"
	if [ -f "$target" -a -f "$target.tsq" -a -f "$target.tsr" ]; then
		echo "$f exists already: .tsq and .tsr files are there, check the timestamp just in case"
		openssl ts -verify -in "${target}.tsr" -queryfile "${target}.tsq" -CAfile $target_path/cacert.pem -untrusted $target_path/tsa.crt || true
		continue
	fi
	echo "Copying $f..."
	cp "$f" "$target"

	echo "Create query..."
	openssl ts -query -data "$target" -no_nonce -sha512 -out "$target.tsq.tmp"

	echo "Get timestamp..."
	touch "${target}.tsr.tmp"
	curl -H "Content-Type: application/timestamp-query" --data-binary "@${target}.tsq.tmp" https://freetsa.org/tsr > "${target}.tsr.tmp"

	echo "Verify timestamp..."
	openssl ts -verify -in "${target}.tsr.tmp" -queryfile "${target}.tsq.tmp" -CAfile $target_path/cacert.pem -untrusted $target_path/tsa.crt

	echo "Rename files..."
	mv "${target}.tsr.tmp" "${target}.tsr"
	mv "${target}.tsq.tmp" "${target}.tsq"
done
popd

# Example run:
#openssl ts -query -data xmlexport-20190410-114627-22.zip -no_nonce -sha512 -out xmlexport-20190410-114627-22.zip.tsq
#curl -H "Content-Type: application/timestamp-query" --data-binary '@xmlexport-20190410-114627-22.zip.tsq' https://freetsa.org/tsr > xmlexport-20190410-114627-22.zip.tsr
#openssl ts -verify -in xmlexport-20190410-114627-22.zip.tsr -queryfile xmlexport-20190410-114627-22.zip.tsq -CAfile cacert.pem -untrusted tsa.crt
