<?php
// Exit if accessed directly
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}
?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo( 'charset' ); ?>" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>

<header class="gudha-header-container" role="banner">

  <!-- LEFT: LOGO -->
  <div class="gudha-logo">
    <a href="<?php echo esc_url( home_url( '/' ) ); ?>" aria-label="Go to homepage">
      <?php 
        if ( function_exists( 'the_custom_logo' ) && has_custom_logo() ) {
          the_custom_logo();
        } else { 
          // Fallback: show site name if no logo
          bloginfo( 'name' ); 
        }
      ?>
    </a>
  </div>

  <!-- CENTER: SITE TITLE -->
  <div class="gudha-site-title">
    <a href="<?php echo esc_url( home_url( '/' ) ); ?>">
      CASSIE MARIE | AUTHOR
    </a>
  </div>

  <!-- RIGHT: HAMBURGER MENU BUTTON -->
  <div class="gudha-hamburger">
    <button id="gudha-menu-toggle" aria-label="Toggle site menu" aria-expanded="false" aria-controls="site-menu">
      &#9776; <!-- classic 3-bar hamburger icon -->
    </button>
  </div>

</header>

<!-- SITE MENU (hidden by default, toggled with JS) -->
<nav id="site-menu" class="hidden" role="navigation" aria-label="Primary Menu">
  <?php
    wp_nav_menu( array(
      'theme_location' => 'primary', // Make sure this is registered in functions.php!
      'menu_class'     => 'nav-menu',
      'container'      => false,
      'fallback_cb'    => false,
    ) );
  ?>
</nav>

<script>
  // BURGER MENU TOGGLE SCRIPT
  (function() {
    const btn = document.getElementById('gudha-menu-toggle');
    const menu = document.getElementById('site-menu');

    btn.addEventListener('click', function() {
      const isExpanded = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', !isExpanded);
      menu.classList.toggle('hidden');
    });
  })();
</script>