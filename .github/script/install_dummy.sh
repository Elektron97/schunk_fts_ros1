#/usr/bin/bash
pwd
ls -alF

# Install Rust
sudo apt-get install -y curl
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
if [ -f "$HOME/.cargo/env" ]; then
	. "$HOME/.cargo/env"
elif [ -f /usr/local/cargo/env ]; then
	. /usr/local/cargo/env
fi

# Build the FTS dummy and make it available for tests
cd schunk_fts_dummy
target_dir="/tmp/schunk_fts_dummy"
CARGO_TARGET_DIR=$target_dir cargo build
echo "Build the FTS dummy here: $(find $target_dir -maxdepth 2)"
