mod output_rate;
mod sensor;
mod tcp;
mod udp;
use tokio::io;

#[tokio::main]
async fn main() -> io::Result<()> {
    let output_rate = output_rate::OutputRateState::default();
    let udp_output_rate = output_rate.clone();

    tokio::spawn(async {
        udp::stream_ft_data(udp_output_rate).await;
    });

    tcp::handle_requests(output_rate).await
}
