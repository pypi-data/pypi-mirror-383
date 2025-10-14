#![allow(
    clippy::too_many_arguments,
    clippy::needless_pass_by_value,
    clippy::module_name_repetitions,
    clippy::significant_drop_tightening,
    clippy::large_enum_variant
)]

mod assets;
mod bytes;
mod camera;
mod mesh;
mod renderer;
mod rocketsim;
mod settings;
mod spectator;
mod udp;

use bevy::{
    image::{ImageAddressMode, ImageSamplerDescriptor},
    log::LogPlugin,
    prelude::*,
    window::PresentMode,
};
use settings::{cache_handler, gui};
use std::{env, fs, io, path::Path};
use tracing::Level;
use zip::ZipArchive;

// Embed cache.zip at compile time
const CACHE_ZIP: &[u8] = include_bytes!("../cache.zip");

/// Extract embedded cache.zip if cache/ directory doesn't exist
fn extract_cache_if_needed() -> io::Result<()> {
    let cache_dir = Path::new("cache");

    // Only extract if cache directory doesn't exist
    if cache_dir.exists() {
        return Ok(());
    }

    println!("Extracting game assets for first run...");

    let cursor = io::Cursor::new(CACHE_ZIP);
    let mut archive = ZipArchive::new(cursor)?;

    for i in 0..archive.len() {
        let mut file = archive.by_index(i)?;
        let outpath = file.mangled_name();

        if file.is_dir() {
            fs::create_dir_all(&outpath)?;
        } else {
            if let Some(p) = outpath.parent() {
                fs::create_dir_all(p)?;
            }
            let mut outfile = fs::File::create(&outpath)?;
            io::copy(&mut file, &mut outfile)?;
        }
    }

    println!("Assets extracted successfully");
    Ok(())
}

#[derive(Clone, Eq, PartialEq, Debug, Hash, Default, States)]
enum GameLoadState {
    #[default]
    Cache,
    Connect,
    FieldExtra,
    Despawn,
    Field,
    None,
}

#[derive(Resource)]
pub struct ServerPort {
    primary_port: u16,
    secondary_port: u16,
}

fn main() {
    // Extract cache on first run
    if let Err(e) = extract_cache_if_needed() {
        eprintln!("Warning: Failed to extract cache: {}", e);
    }

    let mut args = env::args();

    // read the first argument and treat it as the port to connect to (u16)
    let primary_port = args.nth(1).and_then(|s| s.parse::<u16>().ok()).unwrap_or(34254);
    // read the second argument and treat it as the port to bind the UDP socket to (u16)
    let secondary_port = args.next().and_then(|s| s.parse::<u16>().ok()).unwrap_or(45243);

    #[cfg(debug_assertions)]
    assets::umodel::uncook().unwrap();

    App::new()
        .insert_resource(ServerPort {
            primary_port,
            secondary_port,
        })
        .add_plugins((
            DefaultPlugins
                .set(TaskPoolPlugin {
                    task_pool_options: TaskPoolOptions::with_num_threads(if cfg!(feature = "threaded") { 3 } else { 1 }),
                })
                .set(LogPlugin {
                    level: if cfg!(debug_assertions) { Level::INFO } else { Level::ERROR },
                    filter: if cfg!(debug_assertions) {
                        String::from("wgpu=error,naga=warn")
                    } else {
                        String::new()
                    },
                    ..Default::default()
                })
                .set(ImagePlugin {
                    default_sampler: ImageSamplerDescriptor {
                        address_mode_u: ImageAddressMode::Repeat,
                        address_mode_v: ImageAddressMode::Repeat,
                        address_mode_w: ImageAddressMode::Repeat,
                        ..default()
                    },
                })
                .set(WindowPlugin {
                    primary_window: Some(Window {
                        title: "RLViser-rs".into(),
                        present_mode: PresentMode::AutoNoVsync,
                        ..default()
                    }),
                    ..default()
                }),
            cache_handler::CachePlugin,
            camera::CameraPlugin,
            gui::DebugOverlayPlugin,
            mesh::FieldLoaderPlugin,
            udp::RocketSimPlugin,
            assets::AssetsLoaderPlugin,
        ))
        .init_state::<GameLoadState>()
        .run();
}
