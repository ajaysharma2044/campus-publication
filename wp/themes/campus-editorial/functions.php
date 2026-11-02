<?php
/** Campus Editorial theme bootstrap. */
if ( ! defined( 'ABSPATH' ) ) { exit; }

add_action( 'after_setup_theme', function () {
	add_theme_support( 'title-tag' );
	add_theme_support( 'html5', array( 'search-form', 'gallery', 'caption', 'style', 'script' ) );
	add_theme_support( 'post-thumbnails' );
	register_nav_menus( array( 'sections' => 'Section navigation', 'footer' => 'Footer links' ) );
	remove_action( 'wp_head', 'wp_generator' );
	remove_action( 'wp_head', 'print_emoji_detection_script', 7 );
	remove_action( 'wp_print_styles', 'print_emoji_styles' );
} );

add_action( 'wp_enqueue_scripts', function () {
	wp_enqueue_style( 'campus', get_theme_file_uri( 'assets/campus.css' ), array(), wp_get_theme()->get( 'Version' ) );
	if ( is_singular( 'campus_tool' ) ) {
		wp_enqueue_script( 'campus-tools', get_theme_file_uri( 'assets/tools.js' ), array(), wp_get_theme()->get( 'Version' ), array( 'strategy' => 'defer' ) );
	}
	wp_dequeue_style( 'wp-block-library' );
	wp_dequeue_style( 'classic-theme-styles' );
	wp_dequeue_style( 'global-styles' );
} );

add_action( 'wp_head', function () {
	echo '<link rel="preload" href="' . esc_url( get_theme_file_uri( 'assets/fonts/SourceSerif4-Variable.woff2' ) ) . '" as="font" type="font/woff2" crossorigin>' . "\n";
	// Single approved ad loader: only when the ads option is on AND production AND consent cookie present.
	if ( campus_ads_enabled() && isset( $_COOKIE['campus_consent'] ) && 'ads' === $_COOKIE['campus_consent'] ) {
		$pub = get_option( 'campus_adsense_publisher_id' );
		echo '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-' . esc_attr( $pub ) . '" crossorigin="anonymous"></script>' . "\n";
	}
}, 1 );

function campus_ads_enabled(): bool {
	$pub = get_option( 'campus_adsense_publisher_id', '' );
	return 'production' === wp_get_environment_type() && (bool) get_option( 'campus_ads_enabled', false ) && (bool) preg_match( '/^pub-\d{16}$/', $pub );
}
function campus_is_staging(): bool { return 'production' !== wp_get_environment_type(); }
function campus_meta( string $key, $post = null ) {
	$id = $post ? ( is_object( $post ) ? $post->ID : (int) $post ) : get_the_ID();
	return get_post_meta( $id, 'campus_' . $key, true );
}
function campus_meta_json( string $key, $post = null ): array {
	$raw = campus_meta( $key, $post );
	$d = $raw ? json_decode( $raw, true ) : null;
	return is_array( $d ) ? $d : array();
}
/** Approved ad placements by template (SPEC §22). Returns slot HTML or ''. */
function campus_ad_slot( string $placement ): string {
	if ( ! campus_ads_enabled() || ! isset( $_COOKIE['campus_consent'] ) || 'ads' !== $_COOKIE['campus_consent'] ) { return ''; }
	$allowed = array( 'campus_guide' => array( 'after_essentials', 'between_sections' ), 'campus_profile' => array( 'after_facts', 'desktop_sidebar' ), 'campus_topic' => array( 'between_groups' ), 'campus_school' => array( 'between_groups' ), 'campus_comparison' => array( 'after_results' ) );
	if ( ! in_array( $placement, $allowed[ get_post_type() ] ?? array(), true ) ) { return ''; }
	$pub = esc_attr( get_option( 'campus_adsense_publisher_id' ) );
	return '<div class="ad-slot ad-slot--' . esc_attr( $placement ) . '" aria-label="Advertisement"><span class="ad-slot__label">Advertisement</span><ins class="adsbygoogle" style="display:block" data-ad-client="ca-' . $pub . '" data-ad-format="auto" data-full-width-responsive="true"></ins></div>';
}
/** Render the "What to do next", sources and production-note sections from structured meta. */
function campus_next_actions(): void {
	$actions = campus_meta_json( 'next_actions' );
	if ( ! $actions ) { return; }
	echo '<section class="next-actions" aria-labelledby="next-h"><h2 id="next-h" class="section-head" style="border:0;margin-top:0">What to do next</h2><ol>';
	foreach ( $actions as $a ) { echo '<li><a href="' . esc_url( $a['target'] ?? '#' ) . '">' . esc_html( $a['text'] ?? '' ) . '</a></li>'; }
	echo '</ol></section>';
}
function campus_sources(): void {
	$sources = campus_meta_json( 'sources' );
	echo '<section class="sources" aria-labelledby="sources-h"><h2 id="sources-h" class="section-head">Sources and verification</h2>';
	if ( $sources ) {
		echo '<ol>';
		foreach ( $sources as $s ) {
			echo '<li><a href="' . esc_url( $s['url'] ?? '' ) . '" rel="noopener">' . esc_html( $s['title'] ?? ( $s['url'] ?? '' ) ) . '</a> — ' . esc_html( $s['publisher'] ?? '' );
			if ( ! empty( $s['retrieved_at'] ) ) { echo ', retrieved ' . esc_html( wp_date( 'F j, Y', strtotime( $s['retrieved_at'] ) ) ); }
			echo '</li>';
		}
		echo '</ol>';
	} else { echo '<p class="coverage-note">No external sources are cited on this page.</p>'; }
	$note = campus_meta( 'production_note' );
	if ( $note ) { echo '<p class="aside-note">' . esc_html( $note ) . '</p>'; }
	echo '<p class="corrections-link">Spotted an error? <a href="' . esc_url( home_url( '/about/corrections/?page=' . campus_meta( 'external_id' ) ) ) . '">Request a correction</a>.</p></section>';
}
function campus_fact_table(): void {
	$s = campus_meta_json( 'structured' );
	$rows = $s['fact_table'] ?? array();
	if ( ! $rows ) { return; }
	echo '<div class="table-wrap"><table class="facts"><caption>' . esc_html( $s['fact_table_caption'] ?? 'Verified facts' ) . '</caption><thead><tr><th scope="col">Fact</th><th scope="col">Value</th><th scope="col">Status</th></tr></thead><tbody>';
	foreach ( $rows as $r ) {
		$st = $r['status'] ?? 'verified';
		echo '<tr class="' . ( 'unknown' === $st ? 'unknown' : '' ) . '"><th scope="row">' . esc_html( $r['label'] ?? '' ) . '</th><td>' . esc_html( $r['value'] ?? '' ) . ( ! empty( $r['note'] ) ? ' <span class="table-note">' . esc_html( $r['note'] ) . '</span>' : '' ) . '</td><td><span class="evidence-tag evidence-tag--' . esc_attr( $st ) . '">' . esc_html( $st ) . '</span>' . ( ! empty( $r['verified_at'] ) ? ' <span class="meta">checked ' . esc_html( wp_date( 'M j, Y', strtotime( $r['verified_at'] ) ) ) . '</span>' : '' ) . '</td></tr>';
	}
	echo '</tbody></table></div>';
	if ( ! empty( $s['fact_table_footnote'] ) ) { echo '<p class="table-note">' . esc_html( $s['fact_table_footnote'] ) . '</p>'; }
}
