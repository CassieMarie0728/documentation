<?php
// Exit if accessed directly
if ( !defined( 'ABSPATH' ) ) exit;

// Theme Setup
if ( ! function_exists( 'gudha_setup' ) ) {
	add_action( 'after_setup_theme', 'gudha_setup' );
	function gudha_setup() {
		add_editor_style( 'style.css' );
		theme_support_customizations();
		register_nav_menus( array(
			'primary' => __( 'Primary Menu', 'gudha' ),
		) );
	}
}

// Background support
add_action( 'after_setup_theme', 'martanda_background_setup' );
function martanda_background_setup() {
	add_theme_support( "custom-background", array(
		'default-color' => '121212',
		'default-image' => '',
		'default-repeat' => 'repeat',
		'default-position-x' => 'left',
		'default-position-y' => 'top',
		'default-size' => 'auto',
		'default-attachment' => '',
		'wp-head-callback' => '_custom_background_cb',
	) );
}

// Custom font loading for Subway-Novella and Elegant-Typewriter
function gudha_custom_fonts() {
	return "
		@font-face {
			font-family: 'Subway Novella';
			src: url('" . get_stylesheet_directory_uri() . "/fonts/Subway-Novella.ttf') format('truetype');
			font-weight: normal;
			font-style: normal;
			font-display: swap;
		}
		@font-face {
			font-family: 'Elegant Typewriter';
			src: url('" . get_stylesheet_directory_uri() . "/fonts/Elegant-Typewriter.ttf') format('truetype');
			font-weight: normal;
			font-style: normal;
			font-display: swap;
		}
	";
}

function gudha_custom_font_css() {
	return "
		body {
			font-family: 'Elegant Typewriter', monospace;
			color: #a8a9ad;
		}
		h1, h2, h3, h4, h5, h6,
		.site-title,
		.site-description,
		nav a,
		.gudha-site-title,
		.gudha-hamburger button {
			font-family: 'Subway Novella', sans-serif;
			color: #981518;
		}
	";
}

// Combine all custom dynamic styles
if ( ! function_exists( 'gudha_enqueue_parent_dynamic_css' ) ) {
	add_action( 'wp_enqueue_scripts', 'gudha_enqueue_parent_dynamic_css', 50 );
	function gudha_enqueue_parent_dynamic_css() {
		$css = gudha_custom_fonts() . gudha_custom_font_css() . martanda_base_css() . gudha_effect_css();
		wp_add_inline_style( 'martanda-child', $css );
	}
}

// Theme URI
function martanda_theme_uri_link() {
	return 'https://wpkoi.com/gudha-wpkoi-wordpress-theme/';
}

// Customizer noise image
if ( ! function_exists( 'gudha_customize_register' ) ) {
	add_action( 'customize_register', 'gudha_customize_register' );
	function gudha_customize_register( $wp_customize ) {
		$wp_customize->add_section( 'gudha_layout_effects', array(
			'title' => __( 'Background noise', 'gudha' ),
			'priority' => 24,
		) );

		$wp_customize->add_setting( 'gudha_settings[noise_image]', array(
			'default' => get_stylesheet_directory_uri().'/img/gudha-noise.webp',
			'type' => 'option',
			'sanitize_callback' => 'esc_url_raw'
		) );

		$wp_customize->add_control( new WP_Customize_Image_Control(
			$wp_customize,
			'gudha_settings[noise_image]',
			array(
				'label' => __( 'Background noise image', 'gudha' ),
				'section' => 'gudha_layout_effects',
				'priority' => 10,
				'settings' => 'gudha_settings[noise_image]',
				'description' => __( 'Recommended size: 100*100px.', 'gudha' )
			)
		));
	}
}

// Sanitize select inputs
if ( ! function_exists( 'gudha_sanitize_choices' ) ) {
	function gudha_sanitize_choices( $input, $setting ) {
		$input = sanitize_key( $input );
		$choices = $setting->manager->get_control( $setting->id )->choices;
		return ( array_key_exists( $input, $choices ) ? $input : $setting->default );
	}
}

// Custom background noise effect CSS
if ( ! function_exists( 'gudha_effect_css' ) ) {
	function gudha_effect_css() {
		$gudha_settings = get_option( 'gudha_settings' );
		$noise_image = isset( $gudha_settings['noise_image'] ) ? $gudha_settings['noise_image'] : get_stylesheet_directory_uri().'/img/gudha-noise.webp';
		return '.gudha-noise{background: transparent url(' . esc_url( $noise_image ) . ') repeat 0 0;}';
	}
}

// Remove parent's dynamic CSS
if ( ! function_exists( 'gudha_remove_parent_dynamic_css' ) ) {
	add_action( 'init', 'gudha_remove_parent_dynamic_css' );
	function gudha_remove_parent_dynamic_css() {
		remove_action( 'wp_enqueue_scripts', 'martanda_enqueue_dynamic_css', 50 );
	}
}

// Add noise animation container
if ( ! function_exists( 'gudha_noise_holder' ) ) {
	add_action( 'martanda_after_footer_content', 'gudha_noise_holder' );
	function gudha_noise_holder() {
		echo '<div class="gudha-noise"></div>';
	}
}