#!/bin/bash -e
#
# A helper script for gitlab to automatically RFC 3161 timestamp last git commit of each push.
# Uses the freetsa.org service.
# 
# Example usage, assuming gitlab is run as user git and gitlab is installed at /opt/gitlab.
# 1. mkdir /var/lib/git-timestamps
# 2. chown git:git /var/lib/git-timestamps
# 3. cd /var/lib/git-timestamps
# 4. curl -O https://freetsa.org/files/cacert.pem -O https://freetsa.org/files/tsa.crt
# 5. mkdir /opt/gitlab/embedded/service/gitlab-shell/hooks/post-receive.d
# 6. Place this script in /opt/gitlab/embedded/service/gitlab-shell/hooks/post-receive.d/gitlab_timestamp.sh
# 7. Make a commit & push to your git repository. You should see result in git output.
# 8. See files in /var/lib/git-timestamps/<my_project>/
# 9. To verify a signature manually, do:
#    openssl ts -verify -in "/var/lib/git-timestamps/<my-project>/<commit_hash>.tsr" -queryfile "/var/lib/git-timestamps/<my-project>/<commit_hash>.tsq" -CAfile /var/lib/git-timestamps/cacert.pem -untrusted /var/lib/git-timestamps/tsa.crt

repo=$(basename "$PWD")
commits_target="/var/lib/git-timestamps"
target_dir="$commits_target/$repo"
if [ ! -d "$commits_target" ]; then
	echo "output directory not found"
	exit 1
fi

# First, find the last commit of the push. We're not interested in signing all commits, just the last one for each push.
unset commit
while read oldrev newrev ref; do
	commit=$newrev
	true
done

# Make sure the target dir exists
mkdir -p "$target_dir"
target="$target_dir/${commit}.commit"

# Create a file to sign, use -s to omit the actual changes to save space.
# We have SHA1 hash anyway.
git show -s "$commit" > "$target"
echo "Create query..."
openssl ts -query -data "$target" -no_nonce -sha512 -out "$target.tsq.tmp"

echo "Get timestamp..."
curl -H "Content-Type: application/timestamp-query" --data-binary "@${target}.tsq.tmp" https://freetsa.org/tsr > "${target}.tsr.tmp"

echo "Verify timestamp..."
openssl ts -verify -in "${target}.tsr.tmp" -queryfile "${target}.tsq.tmp" -CAfile $commits_target/cacert.pem -untrusted $commits_target/tsa.crt

echo "Rename files..."
mv "${target}.tsr.tmp" "${target}.tsr"
mv "${target}.tsq.tmp" "${target}.tsq"
