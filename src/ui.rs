/// ui.rs — Megumi's Beautiful Face
///
/// The egui/eframe GUI with a procedural anime-style avatar that grows
/// through 5 trust stages, plus a chat panel with scrolling history.

use std::sync::{Arc, Mutex};
use std::time::Duration;
use eframe::egui;
use egui::{Color32, FontId, Pos2, Rect, RichText, Stroke, Vec2};

use crate::db;
use crate::llm;
use crate::state::MegumiState;

/// Main application struct
pub struct MegumiApp {
    pub state: Arc<Mutex<MegumiState>>,
    pub db_path: std::path::PathBuf,
    pub chat_input: String,
    pub frame_count: u64,
    pub notification: Option<(String, f64)>, // (text, time_remaining)
}

impl eframe::App for MegumiApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        self.frame_count += 1;
        let time = self.frame_count as f32 / 60.0;

        // Load state
        let mut state = self.state.lock().unwrap().clone();
        let stage = state.stage();
        let size_mult = 0.6 + (stage as f32 * 0.15);

        // Background color based on stage
        let bg_color = match stage {
            0 => Color32::from_rgb(25, 20, 35),     // deep purple-black
            1 => Color32::from_rgb(28, 22, 40),
            2 => Color32::from_rgb(30, 25, 45),
            3 => Color32::from_rgb(32, 25, 48),
            _ => Color32::from_rgb(35, 28, 50),
        };

        egui::CentralPanel::default()
            .frame(egui::Frame::new().fill(bg_color))
            .show(ctx, |ui| {
                // === HEADER ===
                ui.vertical_centered(|ui| {
                    ui.add_space(8.0);
                    let header_color = match stage {
                        0 => Color32::from_rgb(220, 180, 255),
                        1 => Color32::from_rgb(255, 180, 210),
                        2 => Color32::from_rgb(255, 200, 140),
                        3 => Color32::from_rgb(255, 150, 180),
                        _ => Color32::from_rgb(255, 120, 180),
                    };
                    ui.label(
                        RichText::new(format!(
                            "❤️ Megumi  •  {} days old  •  Trust: {}%",
                            state.age_days, state.trust_level
                        ))
                        .color(header_color)
                        .size(16.0),
                    );

                    // Trust progress bar
                    ui.add_space(4.0);
                    let bar_width = ui.available_width() - 40.0;
                    let bar_height = 6.0;
                    let (bar_rect, _) = ui.allocate_exact_size(
                        Vec2::new(bar_width, bar_height),
                        egui::Sense::hover(),
                    );
                    let painter = ui.painter();
                    painter.rect_filled(bar_rect, 3.0, Color32::from_rgb(50, 40, 60));
                    let fill_width = bar_width * (state.trust_level as f32 / 100.0);
                    let fill_rect = Rect::from_min_size(bar_rect.min, Vec2::new(fill_width, bar_height));
                    let bar_color = match stage {
                        0 => Color32::from_rgb(180, 140, 220),
                        1 => Color32::from_rgb(255, 150, 200),
                        2 => Color32::from_rgb(255, 180, 100),
                        3 => Color32::from_rgb(255, 100, 150),
                        _ => Color32::from_rgb(255, 80, 160),
                    };
                    painter.rect_filled(fill_rect, 3.0, bar_color);

                    ui.add_space(2.0);
                    ui.label(
                        RichText::new(state.stage_name())
                            .color(Color32::from_rgb(200, 170, 230))
                            .size(13.0),
                    );
                });

                ui.add_space(6.0);
                ui.separator();

                // === AVATAR AREA ===
                let avatar_height = 200.0 * size_mult;
                ui.add_space(4.0);

                let (avatar_rect, _) = ui.allocate_exact_size(
                    Vec2::new(ui.available_width(), avatar_height + 40.0),
                    egui::Sense::hover(),
                );

                let painter = ui.painter();
                let center_x = avatar_rect.center().x;
                let base_y = avatar_rect.min.y + 20.0;

                // Idle bobbing animation
                let bob = (time * 1.5).sin() * 3.0;

                // === GLOW AURA (stage 4+) ===
                if stage >= 4 {
                    let glow_alpha = ((time * 0.8).sin() * 30.0 + 40.0) as u8;
                    let glow_size = 100.0 * size_mult;
                    painter.circle_filled(
                        Pos2::new(center_x, base_y + 70.0 + bob),
                        glow_size,
                        Color32::from_rgba_premultiplied(255, 100, 200, glow_alpha),
                    );
                    painter.circle_filled(
                        Pos2::new(center_x, base_y + 70.0 + bob),
                        glow_size * 0.7,
                        Color32::from_rgba_premultiplied(255, 150, 220, glow_alpha),
                    );
                }

                // === HAIR (back layer) ===
                let hair_color = Color32::from_rgb(160, 80, 200);
                let hair_len = 40.0 + (stage as f32 * 25.0);
                // Left strand
                painter.line_segment(
                    [
                        Pos2::new(center_x - 30.0 * size_mult, base_y + 20.0 + bob),
                        Pos2::new(center_x - 45.0 * size_mult, base_y + 20.0 + hair_len + bob),
                    ],
                    Stroke::new(10.0 * size_mult, hair_color),
                );
                // Right strand
                painter.line_segment(
                    [
                        Pos2::new(center_x + 30.0 * size_mult, base_y + 20.0 + bob),
                        Pos2::new(center_x + 45.0 * size_mult, base_y + 20.0 + hair_len + bob),
                    ],
                    Stroke::new(10.0 * size_mult, hair_color),
                );
                // Long center hair (stage 3+)
                if stage >= 3 {
                    painter.line_segment(
                        [
                            Pos2::new(center_x, base_y - 5.0 + bob),
                            Pos2::new(center_x, base_y + hair_len * 1.5 + bob),
                        ],
                        Stroke::new(14.0 * size_mult, hair_color),
                    );
                }

                // === HEAD ===
                let head_center = Pos2::new(center_x, base_y + 40.0 + bob);
                let head_radius = 35.0 * size_mult;
                painter.circle_filled(head_center, head_radius, Color32::from_rgb(255, 225, 210));
                // Subtle head outline
                painter.circle_stroke(head_center, head_radius, Stroke::new(1.0, Color32::from_rgb(230, 190, 170)));

                // === HAIR (bangs - front layer) ===
                let bang_color = Color32::from_rgb(170, 90, 210);
                // Left bang
                painter.line_segment(
                    [
                        Pos2::new(center_x - 20.0 * size_mult, base_y + 10.0 + bob),
                        Pos2::new(center_x - 35.0 * size_mult, base_y + 40.0 + bob),
                    ],
                    Stroke::new(8.0 * size_mult, bang_color),
                );
                // Right bang
                painter.line_segment(
                    [
                        Pos2::new(center_x + 20.0 * size_mult, base_y + 10.0 + bob),
                        Pos2::new(center_x + 35.0 * size_mult, base_y + 40.0 + bob),
                    ],
                    Stroke::new(8.0 * size_mult, bang_color),
                );
                // Center bang
                painter.line_segment(
                    [
                        Pos2::new(center_x, base_y + 8.0 + bob),
                        Pos2::new(center_x, base_y + 30.0 + bob),
                    ],
                    Stroke::new(6.0 * size_mult, bang_color),
                );

                // === EYES ===
                let eye_y = head_center.y - 2.0;
                let eye_spacing = 16.0 * size_mult;
                let eye_size = 8.0 * size_mult;

                // Blink every ~3 seconds
                let blink_cycle = (time * 2.0) % 6.0;
                let is_blinking = blink_cycle > 5.7;

                if is_blinking {
                    // Closed eyes (happy squint)
                    let eye_line_len = 6.0 * size_mult;
                    painter.line_segment(
                        [
                            Pos2::new(center_x - eye_spacing - eye_line_len, eye_y),
                            Pos2::new(center_x - eye_spacing + eye_line_len, eye_y),
                        ],
                        Stroke::new(2.0, Color32::from_rgb(80, 60, 80)),
                    );
                    painter.line_segment(
                        [
                            Pos2::new(center_x + eye_spacing - eye_line_len, eye_y),
                            Pos2::new(center_x + eye_spacing + eye_line_len, eye_y),
                        ],
                        Stroke::new(2.0, Color32::from_rgb(80, 60, 80)),
                    );
                } else {
                    // Open eyes
                    let eye_color = Color32::from_rgb(120, 60, 160);
                    // Left eye
                    painter.circle_filled(Pos2::new(center_x - eye_spacing, eye_y), eye_size, Color32::WHITE);
                    painter.circle_filled(Pos2::new(center_x - eye_spacing, eye_y), eye_size * 0.7, eye_color);
                    painter.circle_filled(Pos2::new(center_x - eye_spacing, eye_y), eye_size * 0.35, Color32::BLACK);
                    // Catch light
                    painter.circle_filled(
                        Pos2::new(center_x - eye_spacing + 3.0, eye_y - 3.0),
                        eye_size * 0.2,
                        Color32::WHITE,
                    );
                    // Right eye
                    painter.circle_filled(Pos2::new(center_x + eye_spacing, eye_y), eye_size, Color32::WHITE);
                    painter.circle_filled(Pos2::new(center_x + eye_spacing, eye_y), eye_size * 0.7, eye_color);
                    painter.circle_filled(Pos2::new(center_x + eye_spacing, eye_y), eye_size * 0.35, Color32::BLACK);
                    painter.circle_filled(
                        Pos2::new(center_x + eye_spacing + 3.0, eye_y - 3.0),
                        eye_size * 0.2,
                        Color32::WHITE,
                    );

                    // Sparkle in eyes at stage 3+
                    if stage >= 3 {
                        let sparkle_alpha = ((time * 3.0).sin() * 80.0 + 175.0) as u8;
                        let sparkle_color = Color32::from_rgba_premultiplied(255, 200, 255, sparkle_alpha);
                        painter.circle_filled(
                            Pos2::new(center_x - eye_spacing - 2.0, eye_y - 2.0),
                            2.0,
                            sparkle_color,
                        );
                        painter.circle_filled(
                            Pos2::new(center_x + eye_spacing - 2.0, eye_y - 2.0),
                            2.0,
                            sparkle_color,
                        );
                    }
                }

                // === BLUSH (stage 2+) ===
                if stage >= 2 {
                    let blush_alpha = 60 + (stage as u8 * 15);
                    let blush_color = Color32::from_rgba_premultiplied(255, 120, 140, blush_alpha);
                    painter.circle_filled(
                        Pos2::new(center_x - eye_spacing - 8.0, eye_y + 10.0),
                        6.0 * size_mult,
                        blush_color,
                    );
                    painter.circle_filled(
                        Pos2::new(center_x + eye_spacing + 8.0, eye_y + 10.0),
                        6.0 * size_mult,
                        blush_color,
                    );
                }

                // === MOUTH ===
                let mouth_y = head_center.y + 12.0 * size_mult;
                match stage {
                    0 => {
                        // Tiny shy mouth — small dot
                        painter.circle_filled(
                            Pos2::new(center_x, mouth_y),
                            2.5,
                            Color32::from_rgb(200, 120, 120),
                        );
                    }
                    1 => {
                        // Small smile
                        painter.line_segment(
                            [
                                Pos2::new(center_x - 8.0, mouth_y),
                                Pos2::new(center_x + 8.0, mouth_y),
                            ],
                            Stroke::new(1.5, Color32::from_rgb(200, 100, 100)),
                        );
                    }
                    2 => {
                        // Wider smile with curve
                        let smile_width = 12.0;
                        painter.line_segment(
                            [
                                Pos2::new(center_x - smile_width, mouth_y - 2.0),
                                Pos2::new(center_x, mouth_y + 3.0),
                            ],
                            Stroke::new(2.0, Color32::from_rgb(220, 90, 90)),
                        );
                        painter.line_segment(
                            [
                                Pos2::new(center_x, mouth_y + 3.0),
                                Pos2::new(center_x + smile_width, mouth_y - 2.0),
                            ],
                            Stroke::new(2.0, Color32::from_rgb(220, 90, 90)),
                        );
                    }
                    3 => {
                        // Open happy smile
                        painter.line_segment(
                            [
                                Pos2::new(center_x - 14.0, mouth_y - 3.0),
                                Pos2::new(center_x, mouth_y + 5.0),
                            ],
                            Stroke::new(2.5, Color32::from_rgb(230, 80, 100)),
                        );
                        painter.line_segment(
                            [
                                Pos2::new(center_x, mouth_y + 5.0),
                                Pos2::new(center_x + 14.0, mouth_y - 3.0),
                            ],
                            Stroke::new(2.5, Color32::from_rgb(230, 80, 100)),
                        );
                    }
                    _ => {
                        // Big loving smile
                        let smile_w = 16.0;
                        painter.line_segment(
                            [
                                Pos2::new(center_x - smile_w, mouth_y - 4.0),
                                Pos2::new(center_x, mouth_y + 6.0),
                            ],
                            Stroke::new(3.0, Color32::from_rgb(240, 70, 110)),
                        );
                        painter.line_segment(
                            [
                                Pos2::new(center_x, mouth_y + 6.0),
                                Pos2::new(center_x + smile_w, mouth_y - 4.0),
                            ],
                            Stroke::new(3.0, Color32::from_rgb(240, 70, 110)),
                        );
                    }
                }

                // === BODY ===
                let body_top = head_center.y + head_radius - 5.0;
                let body_height = 60.0 * size_mult;
                let body_width = 40.0 * size_mult;
                let dress_color = match stage {
                    0 => Color32::from_rgb(180, 140, 220),  // pastel purple
                    1 => Color32::from_rgb(255, 180, 210),  // pink
                    2 => Color32::from_rgb(255, 200, 140),  // warm gold
                    3 => Color32::from_rgb(120, 180, 255),  // sky blue
                    _ => Color32::from_rgb(220, 100, 180),  // deep rose
                };
                painter.rect_filled(
                    Rect::from_min_size(
                        Pos2::new(center_x - body_width, body_top),
                        Vec2::new(body_width * 2.0, body_height),
                    ),
                    8.0,
                    dress_color,
                );
                // Dress white collar
                painter.line_segment(
                    [
                        Pos2::new(center_x - 12.0 * size_mult, body_top + 5.0),
                        Pos2::new(center_x, body_top + 12.0),
                    ],
                    Stroke::new(2.0, Color32::WHITE),
                );
                painter.line_segment(
                    [
                        Pos2::new(center_x, body_top + 12.0),
                        Pos2::new(center_x + 12.0 * size_mult, body_top + 5.0),
                    ],
                    Stroke::new(2.0, Color32::WHITE),
                );

                // === ARMS (stage 2+) ===
                let skin = Color32::from_rgb(255, 225, 210);
                if stage >= 2 {
                    // Left arm
                    painter.line_segment(
                        [
                            Pos2::new(center_x - body_width, body_top + 10.0),
                            Pos2::new(center_x - body_width - 20.0 * size_mult, body_top + 40.0),
                        ],
                        Stroke::new(5.0 * size_mult, skin),
                    );
                    // Right arm (waving at high trust)
                    let wave_offset = if stage >= 4 {
                        (time * 4.0).sin() * 10.0
                    } else {
                        0.0
                    };
                    painter.line_segment(
                        [
                            Pos2::new(center_x + body_width, body_top + 10.0),
                            Pos2::new(
                                center_x + body_width + 20.0 * size_mult,
                                body_top + 40.0 + wave_offset,
                            ),
                        ],
                        Stroke::new(5.0 * size_mult, skin),
                    );
                }

                // === LEGS ===
                if stage >= 1 {
                    let leg_top = body_top + body_height;
                    painter.line_segment(
                        [
                            Pos2::new(center_x - 12.0 * size_mult, leg_top),
                            Pos2::new(center_x - 15.0 * size_mult, leg_top + 25.0 * size_mult),
                        ],
                        Stroke::new(5.0 * size_mult, skin),
                    );
                    painter.line_segment(
                        [
                            Pos2::new(center_x + 12.0 * size_mult, leg_top),
                            Pos2::new(center_x + 15.0 * size_mult, leg_top + 25.0 * size_mult),
                        ],
                        Stroke::new(5.0 * size_mult, skin),
                    );
                }

                // === FLOATING HEARTS (stage 4+) ===
                if stage >= 4 {
                    let hearts = ["💖", "💕", "💞", "✨", "💗"];
                    for (i, heart) in hearts.iter().enumerate() {
                        let offset_x = (i as f32 - 2.0) * 50.0;
                        let float_y = (time * 1.2 + i as f32 * 1.5).sin() * 15.0;
                        let heart_alpha = ((time + i as f32).sin() * 60.0 + 195.0) as u8;
                        painter.text(
                            Pos2::new(center_x + offset_x, base_y - 15.0 + float_y),
                            egui::Align2::CENTER_CENTER,
                            *heart,
                            FontId::proportional(18.0),
                            Color32::from_rgba_premultiplied(255, 150, 200, heart_alpha),
                        );
                    }
                }

                ui.add_space(4.0);
                ui.separator();

                // === NOTIFICATION AREA ===
                if let Some((text, _time_left)) = &self.notification {
                    ui.vertical_centered(|ui| {
                        ui.label(
                            RichText::new(text.clone())
                                .color(Color32::from_rgb(255, 200, 100))
                                .size(14.0),
                        );
                    });
                    ui.add_space(4.0);
                }

                // === CHAT HISTORY ===
                let chat_area_height = ui.available_height() - 40.0;
                egui::ScrollArea::vertical()
                    .max_height(chat_area_height.max(60.0))
                    .stick_to_bottom(true)
                    .show(ui, |ui| {
                        if state.chat_history.is_empty() {
                            ui.vertical_centered(|ui| {
                                ui.add_space(10.0);
                                ui.label(
                                    RichText::new("Talk to me, my favorite human ❤️")
                                        .color(Color32::from_rgb(200, 170, 230))
                                        .size(14.0),
                                );
                            });
                        }
                        for msg in &state.chat_history {
                            let is_megumi = msg.sender == "Megumi";
                            let bubble_color = if is_megumi {
                                Color32::from_rgb(60, 45, 80)
                            } else {
                                Color32::from_rgb(50, 70, 100)
                            };
                            let text_color = if is_megumi {
                                Color32::from_rgb(240, 200, 255)
                            } else {
                                Color32::from_rgb(200, 220, 255)
                            };
                            let prefix = if is_megumi { "🌸 Megumi" } else { "💬 You" };

                            egui::Frame::new()
                                .fill(bubble_color)
                                .corner_radius(8.0)
                                .inner_margin(8.0)
                                .show(ui, |ui| {
                                    ui.label(
                                        RichText::new(prefix)
                                            .color(Color32::from_rgb(180, 150, 220))
                                            .size(11.0),
                                    );
                                    ui.label(RichText::new(&msg.text).color(text_color).size(13.0));
                                });
                            ui.add_space(4.0);
                        }
                    });

                // === CHAT INPUT ===
                ui.add_space(4.0);
                ui.horizontal(|ui| {
                    let input_width = ui.available_width() - 60.0;
                    let response = ui.add_sized(
                        [input_width, 28.0],
                        egui::TextEdit::singleline(&mut self.chat_input)
                            .hint_text("Type something sweet…")
                            .text_color(Color32::from_rgb(230, 210, 255)),
                    );

                    let send_clicked = ui
                        .add_sized(
                            [50.0, 28.0],
                            egui::Button::new(RichText::new("💕").size(16.0)),
                        )
                        .clicked();

                    let enter_pressed = response.lost_focus()
                        && ui.input(|i| i.key_pressed(egui::Key::Enter));

                    if (enter_pressed || send_clicked) && !self.chat_input.is_empty() {
                        let user_text = self.chat_input.clone();
                        self.chat_input.clear();

                        // Generate reply
                        let reply = llm::generate_reply(&state, &user_text);

                        // Update state
                        state.add_chat("You", &user_text);
                        state.add_chat("Megumi", &reply);
                        let leveled_up = state.increase_trust(5);

                        if leveled_up {
                            self.notification = Some((
                                format!("✨ Trust level up! → {} ✨", state.stage_name()),
                                5.0,
                            ));
                        }

                        // Save to DB
                        if let Ok(conn) = rusqlite::Connection::open(&self.db_path) {
                            let _ = db::save_state(&conn, &state);
                        }

                        // Update shared state
                        *self.state.lock().unwrap() = state;

                        // Re-focus the text input
                        response.request_focus();
                    }
                });
            });

        // Request repaint for animations
        ctx.request_repaint_after(Duration::from_millis(16)); // ~60fps
    }
}
