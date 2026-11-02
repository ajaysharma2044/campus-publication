<?php get_header(); ?>
<div class="container"><article class="article">
<?php if ( is_search() ) : ?>
	<h1>Search</h1>
	<form class="search-form measure" role="search" method="get" action="<?php echo esc_url( home_url( '/' ) ); ?>"><label class="visually-hidden" for="s">Search</label><input id="s" type="search" name="s" value="<?php echo esc_attr( get_search_query() ); ?>" placeholder="School, building, program, topic"><button class="btn" type="submit">Search</button></form>
<?php elseif ( is_post_type_archive() ) : ?><h1><?php post_type_archive_title(); ?></h1>
<?php else : ?><h1><?php echo esc_html( get_bloginfo( 'name' ) ); ?></h1><?php endif; ?>
<?php if ( have_posts() ) : ?><ul class="story-list"><?php while ( have_posts() ) : the_post(); ?><li><p class="eyebrow"><?php echo esc_html( get_post_type_object( get_post_type() )->label ); ?></p><h3><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3><?php if ( has_excerpt() ) : ?><p><?php echo esc_html( get_the_excerpt() ); ?></p><?php endif; ?></li><?php endwhile; ?></ul>
<?php elseif ( is_search() ) : ?><div class="empty"><h2>No verified pages match “<?php echo esc_html( get_search_query() ); ?>”</h2><p class="coverage-note">Coverage is school-specific. Try the school's name, or browse <a href="<?php echo esc_url( home_url( '/schools/' ) ); ?>">schools with coverage</a>.</p></div>
<?php else : ?><div class="typographic-cover"><p class="big">Nothing published yet.</p><p class="small">The first verified guides appear here when they pass review. No placeholder stories are shown.</p></div><?php endif; ?>
</article></div>
<?php get_footer();
