<?php
/**
 * Plugin Name: Campus Core
 * Description: Structured publishing for the national college information publication: post types keyed by immutable worker IDs, idempotent REST upsert by external id + content hash, redirects, sitemap/indexing controls, ads.txt. No page builder.
 * Version: 0.1.0
 * Requires PHP: 8.1
 * License: GPL-2.0-or-later
 */

if ( ! defined( 'ABSPATH' ) ) { exit; }

define( 'CAMPUS_CORE_VERSION', '0.1.0' );

final class Campus_Core {
	const POST_TYPES = array(
		'campus_school'     => array( 'label' => 'Schools', 'slug' => 'schools', 'has_archive' => true ),
		'campus_topic'      => array( 'label' => 'Topic hubs', 'slug' => 'topic', 'has_archive' => false ),
		'campus_profile'    => array( 'label' => 'Entity profiles', 'slug' => 'profile', 'has_archive' => false ),
		'campus_guide'      => array( 'label' => 'Guides', 'slug' => 'guide', 'has_archive' => false ),
		'campus_comparison' => array( 'label' => 'Comparisons', 'slug' => 'compare', 'has_archive' => false ),
		'campus_tool'       => array( 'label' => 'Tools', 'slug' => 'tools', 'has_archive' => true ),
		'campus_policy'     => array( 'label' => 'Policies', 'slug' => 'about', 'has_archive' => false ),
	);
	const META = array( 'campus_external_id', 'campus_content_hash', 'campus_institution_id', 'campus_campus_id', 'campus_topic_key', 'campus_entity_id', 'campus_path', 'campus_version_no', 'campus_byline', 'campus_production_note', 'campus_structured', 'campus_sources', 'campus_next_actions', 'campus_noindex', 'campus_material_updated_at', 'campus_audience' );

	public static function init(): void {
		add_action( 'init', array( __CLASS__, 'register_types' ) );
		add_action( 'rest_api_init', array( __CLASS__, 'register_routes' ) );
		add_action( 'template_redirect', array( __CLASS__, 'handle_redirects' ), 1 );
		add_filter( 'post_type_link', array( __CLASS__, 'permalink_from_path' ), 10, 2 );
		add_action( 'parse_request', array( __CLASS__, 'route_path' ), 1 );
		add_action( 'init', array( __CLASS__, 'ads_txt_rewrite' ) );
		add_filter( 'wp_sitemaps_post_types', array( __CLASS__, 'sitemap_post_types' ) );
		add_filter( 'wp_sitemaps_add_provider', fn( $provider, $name ) => in_array( $name, array( 'users', 'taxonomies' ), true ) ? false : $provider, 10, 2 );
		add_filter( 'wp_sitemaps_posts_query_args', array( __CLASS__, 'sitemap_query_args' ), 10, 2 );
		add_filter( 'wp_robots', array( __CLASS__, 'robots' ) );
		add_filter( 'get_canonical_url', array( __CLASS__, 'canonical' ), 10, 2 );
		add_action( 'wp_head', array( __CLASS__, 'structured_data' ), 5 );
		add_filter( 'kses_allowed_protocols', fn( $p ) => array_values( array_unique( array_merge( $p, array( 'https', 'http', 'mailto' ) ) ) ) );
	}

	public static function register_types(): void {
		foreach ( self::POST_TYPES as $type => $cfg ) {
			register_post_type( $type, array(
				'label'        => $cfg['label'],
				'public'       => true,
				'show_in_rest' => true,
				'has_archive'  => $cfg['has_archive'],
				'rewrite'      => array( 'slug' => $cfg['slug'], 'with_front' => false ),
				'supports'     => array( 'title', 'editor', 'excerpt', 'revisions', 'custom-fields' ),
				'menu_icon'    => 'dashicons-welcome-learn-more',
			) );
			foreach ( self::META as $key ) {
				register_post_meta( $type, $key, array( 'show_in_rest' => true, 'single' => true, 'type' => 'string', 'auth_callback' => fn() => current_user_can( 'edit_posts' ) ) );
			}
		}
	}

	/* ---------------------------------------------------------------- REST */
	public static function register_routes(): void {
		register_rest_route( 'campus/v1', '/upsert', array(
			'methods'             => 'POST',
			'callback'            => array( __CLASS__, 'rest_upsert' ),
			'permission_callback' => fn() => current_user_can( 'edit_posts' ),
			'args'                => array(
				'external_id'  => array( 'required' => true, 'type' => 'string' ),
				'content_hash' => array( 'required' => true, 'type' => 'string' ),
				'post_type'    => array( 'required' => true, 'type' => 'string', 'enum' => array_keys( self::POST_TYPES ) ),
				'title'        => array( 'required' => true, 'type' => 'string' ),
				'slug'         => array( 'required' => true, 'type' => 'string' ),
				'path'         => array( 'required' => true, 'type' => 'string' ),
				'content_html' => array( 'required' => true, 'type' => 'string' ),
				'status'       => array( 'type' => 'string', 'enum' => array( 'draft', 'publish' ), 'default' => 'draft' ),
				'meta'         => array( 'type' => 'object', 'default' => array() ),
			),
		) );
		register_rest_route( 'campus/v1', '/redirect', array(
			'methods'             => 'POST',
			'callback'            => array( __CLASS__, 'rest_redirect' ),
			'permission_callback' => fn() => current_user_can( 'edit_posts' ),
		) );
		register_rest_route( 'campus/v1', '/status', array(
			'methods'             => 'GET',
			'callback'            => fn() => array( 'plugin' => CAMPUS_CORE_VERSION, 'post_types' => array_keys( self::POST_TYPES ), 'env' => wp_get_environment_type() ),
			'permission_callback' => '__return_true',
		) );
	}

	public static function find_by_external_id( string $external_id ): ?int {
		$q = new WP_Query( array( 'post_type' => array_keys( self::POST_TYPES ), 'post_status' => 'any', 'meta_key' => 'campus_external_id', 'meta_value' => $external_id, 'fields' => 'ids', 'posts_per_page' => 1, 'no_found_rows' => true ) );
		return $q->posts ? (int) $q->posts[0] : null;
	}

	/** Idempotent upsert: same external id + same hash → no write (changed=false). */
	public static function rest_upsert( WP_REST_Request $r ) {
		$external_id = sanitize_text_field( $r['external_id'] );
		$hash        = sanitize_text_field( $r['content_hash'] );
		$existing    = self::find_by_external_id( $external_id );
		if ( $existing && get_post_meta( $existing, 'campus_content_hash', true ) === $hash ) {
			return array( 'id' => $existing, 'created' => false, 'changed' => false, 'url' => get_permalink( $existing ) );
		}
		$content = wp_kses_post( $r['content_html'] ); // allowlist sanitisation before storage (SPEC §27)
		$postarr = array(
			'post_type'    => $r['post_type'],
			'post_title'   => sanitize_text_field( $r['title'] ),
			'post_name'    => sanitize_title( $r['slug'] ),
			'post_content' => $content,
			'post_status'  => $r['status'] ?: 'draft',
			'post_excerpt' => isset( $r['meta']['deck'] ) ? sanitize_text_field( $r['meta']['deck'] ) : '',
		);
		if ( $existing ) {
			$postarr['ID'] = $existing;
			$old_path      = get_post_meta( $existing, 'campus_path', true );
			$id            = wp_update_post( $postarr, true );
			if ( ! is_wp_error( $id ) && $old_path && $old_path !== $r['path'] ) {
				self::add_redirect( $old_path, $r['path'] ); // path change → preserve old URL
			}
		} else {
			$id = wp_insert_post( $postarr, true );
		}
		if ( is_wp_error( $id ) ) {
			return new WP_Error( 'campus_upsert_failed', $id->get_error_message(), array( 'status' => 400 ) );
		}
		update_post_meta( $id, 'campus_external_id', $external_id );
		update_post_meta( $id, 'campus_content_hash', $hash );
		update_post_meta( $id, 'campus_path', sanitize_text_field( $r['path'] ) );
		foreach ( (array) $r['meta'] as $k => $v ) {
			$key = 'campus_' . sanitize_key( $k );
			if ( in_array( $key, self::META, true ) ) {
				update_post_meta( $id, $key, is_scalar( $v ) ? sanitize_text_field( (string) $v ) : wp_json_encode( $v ) );
			}
		}
		return array( 'id' => $id, 'created' => ! $existing, 'changed' => true, 'url' => get_permalink( $id ) );
	}

	/* ---------------------------------------------------------------- URL model: /schools/{school}/{topic}/{slug}/ (SPEC §18) */
	public static function permalink_from_path( string $link, WP_Post $post ): string {
		if ( ! isset( self::POST_TYPES[ $post->post_type ] ) ) { return $link; }
		$path = get_post_meta( $post->ID, 'campus_path', true );
		return $path ? home_url( $path ) : $link;
	}
	/** Resolve a request whose path equals a stored campus_path to that post (immutable id behind the slug). */
	public static function route_path( WP $wp ): void {
		$path = wp_parse_url( $_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH ) ?: '/';
		if ( '/' === $path || str_starts_with( $path, '/wp-' ) ) { return; }
		$path = trailingslashit( $path );
		$q = new WP_Query( array( 'post_type' => array_keys( self::POST_TYPES ), 'post_status' => 'publish', 'meta_key' => 'campus_path', 'meta_value' => $path, 'fields' => 'ids', 'posts_per_page' => 1, 'no_found_rows' => true ) );
		if ( $q->posts ) {
			$post = get_post( $q->posts[0] );
			$wp->query_vars = array( 'post_type' => $post->post_type, 'name' => $post->post_name, 'p' => $post->ID );
			$wp->matched_rule = 'campus_path';
		}
	}

	/* ---------------------------------------------------------------- redirects */
	public static function add_redirect( string $from, string $to ): void {
		$map          = get_option( 'campus_redirects', array() );
		$map[ untrailingslashit( $from ) ] = $to;
		update_option( 'campus_redirects', $map, false );
	}
	public static function rest_redirect( WP_REST_Request $r ) {
		$from = sanitize_text_field( $r['from'] ); $to = sanitize_text_field( $r['to'] );
		if ( ! $from || ! $to || $from === $to || ! str_starts_with( $from, '/' ) || ! str_starts_with( $to, '/' ) ) {
			return new WP_Error( 'campus_bad_redirect', 'from/to must be distinct site-relative paths', array( 'status' => 400 ) );
		}
		self::add_redirect( $from, $to );
		return array( 'ok' => true );
	}
	public static function handle_redirects(): void {
		// Duplicate-URL guard: a structured post reached by its WP slug path redirects to its canonical campus_path.
		if ( is_singular( array_keys( self::POST_TYPES ) ) ) {
			$canon = get_post_meta( get_the_ID(), 'campus_path', true );
			$req   = trailingslashit( wp_parse_url( $_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH ) ?: '/' );
			if ( $canon && $req !== $canon ) { wp_safe_redirect( home_url( $canon ), 301 ); exit; }
		}
		$map = get_option( 'campus_redirects', array() );
		if ( ! $map ) { return; }
		$path = untrailingslashit( wp_parse_url( $_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH ) ?: '/' );
		if ( isset( $map[ $path ] ) ) {
			wp_safe_redirect( home_url( $map[ $path ] ), 301 );
			exit;
		}
	}

	/* ---------------------------------------------------------------- SEO controls */
	public static function sitemap_post_types( array $types ): array {
		$out = array();
		foreach ( $types as $name => $obj ) { if ( isset( self::POST_TYPES[ $name ] ) ) { $out[ $name ] = $obj; } }
		return $out; // only our structured types; never default posts/pages/attachments
	}
	public static function sitemap_query_args( array $args, string $post_type ): array {
		$args['meta_query'] = array( 'relation' => 'OR', array( 'key' => 'campus_noindex', 'compare' => 'NOT EXISTS' ), array( 'key' => 'campus_noindex', 'value' => '1', 'compare' => '!=' ) );
		return $args;
	}
	public static function robots( array $robots ): array {
		if ( is_search() || is_paged() || ( isset( $_GET['compare'] ) || isset( $_GET['sort'] ) || isset( $_GET['filter'] ) ) ) { $robots['noindex'] = true; $robots['follow'] = true; }
		if ( is_singular() && get_post_meta( get_the_ID(), 'campus_noindex', true ) === '1' ) { $robots['noindex'] = true; $robots['follow'] = true; }
		if ( 'production' !== wp_get_environment_type() ) { $robots['noindex'] = true; $robots['nofollow'] = true; } // staging never indexed
		return $robots;
	}
	public static function canonical( $url, $post ) {
		$path = get_post_meta( $post->ID, 'campus_path', true );
		return $path ? home_url( $path ) : $url;
	}
	public static function structured_data(): void {
		if ( ! is_singular( array( 'campus_guide', 'campus_profile', 'campus_comparison' ) ) ) { return; }
		$p = get_post();
		$data = array(
			'@context' => 'https://schema.org', '@type' => 'Article', 'headline' => get_the_title( $p ), 'description' => get_the_excerpt( $p ),
			'datePublished' => get_the_date( 'c', $p ), 'dateModified' => get_post_meta( $p->ID, 'campus_material_updated_at', true ) ?: get_the_date( 'c', $p ),
			'author' => array( '@type' => 'Organization', 'name' => get_bloginfo( 'name' ) . ' — ' . ( get_post_meta( $p->ID, 'campus_byline', true ) ?: 'Publication desk' ) ),
			'publisher' => array( '@type' => 'Organization', 'name' => get_bloginfo( 'name' ) ),
		);
		echo '<script type="application/ld+json">' . wp_json_encode( $data, JSON_UNESCAPED_SLASHES ) . '</script>' . "\n";
	}

	/* ---------------------------------------------------------------- ads.txt */
	public static function ads_txt_rewrite(): void {
		add_action( 'parse_request', function ( $wp ) {
			if ( ( $_SERVER['REQUEST_URI'] ?? '' ) === '/ads.txt' ) {
				header( 'Content-Type: text/plain; charset=utf-8' );
				$pub = get_option( 'campus_adsense_publisher_id', '' );
				echo ( $pub && 'production' === wp_get_environment_type() ) ? "google.com, {$pub}, DIRECT, f08c47fec0942fa0\n" : "# ads.txt: advertising not enabled on this environment\n";
				exit;
			}
		} );
	}
}
Campus_Core::init();
