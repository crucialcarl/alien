import sys
import pygame
from bullet import Bullet
from alien import Alien
from time import sleep

def check_keydown_events(event, ai_settings, screen, ship, bullets):
  """ Respond to keypresses"""
  if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
    sys.exit()
  elif event.key == pygame.K_RIGHT:
    ship.moving_right = True
  elif event.key == pygame.K_LEFT:
    ship.moving_left = True
  elif event.key == pygame.K_UP:
    ship.moving_up = True
  elif event.key == pygame.K_DOWN:
    ship.moving_down = True
  elif event.key == pygame.K_SPACE:
    # create a new bullet
    if len(bullets) < ai_settings.bullets_max:
      new_bullet = Bullet(screen, ai_settings, ship)
      bullets.add(new_bullet)

def check_keyup_events(event, ship):
  """ Respond to keyrelease"""
  if event.key == pygame.K_RIGHT:
    ship.moving_right = False
  elif event.key == pygame.K_LEFT:
    ship.moving_left = False
  elif event.key == pygame.K_UP:
    ship.moving_up = False
  elif event.key == pygame.K_DOWN:
    ship.moving_down = False


def check_events(ai_settings, screen, ship, bullets):
  """ Respond to keypresses and mouse events """
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      sys.exit()
    elif event.type == pygame.KEYDOWN:
      check_keydown_events(event,ai_settings, screen, ship, bullets)
    elif event.type == pygame.KEYUP:
      check_keyup_events(event,ship)

def update_screen(ai_settings, screen, bg, ship, aliens, bullets):
  """ Update images on the screen and flip to new screen """
  # Redraw the screen during each pass through the loop
  screen.blit(bg, [0,0])
 
  # redraw all bullets behind ship and aliens
  for bullet in bullets.sprites():
    bullet.draw_bullet()
  ship.blitme()
  aliens.draw(screen)

  # Make the most recently drawn screen visible
  pygame.display.flip()

def update_bullets(ai_settings, screen, ship, aliens, bullets):
  """ update position of bullets """
  bullets.update()
  
  # get rid of old bullets
  for bullet in bullets.copy():
    if bullet.rect.bottom <= 0:
      bullets.remove(bullet)
  check_bullet_alien_collisions(ai_settings, screen, ship, aliens, bullets)

def check_bullet_alien_collisions(ai_settings, screen, ship, aliens, bullets):
  # get rid of all bullets if there are collisions
  collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
  if len(aliens) == 0:
    # destroy existing bullets and create a new fleet
    bullets.empty()
    create_fleet(ai_settings, screen, ship, aliens) 

def get_number_aliens_x(ai_settings, alien_width):
  """ determine the number of aliens that fit in a row"""
  available_space_x = ai_settings.screen_width - 2 * alien_width
  number_aliens_x = int(available_space_x / (2 * alien_width))
  return number_aliens_x
  
def get_number_rows(ai_settings, ship_height, alien_height):
  """ determine number of rows of aliens that fit"""
  available_space_y = (ai_settings.screen_height - (3 * alien_height) - ship_height)
  number_rows = int(available_space_y / (2 * alien_height))
  return number_rows

def create_alien(ai_settings, screen, aliens, alien_number, row_number):
  """ create an alien and place it in the row"""
  alien = Alien(ai_settings, screen)
  alien_width = alien.rect.width
  alien.x = alien_width + 2 * alien_width * alien_number
  alien.rect.x = alien.x
  alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
  aliens.add(alien)

def create_fleet(ai_settings, screen, ship, aliens):
  """ Create a fleet of aliens"""
  # create an alien and find the number of aliens in a row
  # spacing between each alien is equal to one alien width
  alien = Alien(ai_settings, screen)
  number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
  number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)
 
  # create the fleet of aliens
  for row_number in range(number_rows):
    for alien_number in range(number_aliens_x):
      create_alien(ai_settings, screen, aliens, alien_number, row_number)

def check_fleet_edges(ai_settings, aliens):
  """ Respond appropraitely if any aliens have reached an edge"""
  for alien in aliens.sprites():
    if alien.check_edge():
      change_fleet_direction(ai_settings, aliens)
      break

def change_fleet_direction(ai_settings, aliens):
  """ Drop the entire fleet and change direction"""
  for alien in aliens.sprites():
    alien.rect.y += ai_settings.fleet_drop_speed
  ai_settings.fleet_direction *= -1

def update_aliens(ai_settings, stats, screen, ship, aliens, bullets):
  """ Check if fleet is at edge, and then update positions of all aliens """
  check_fleet_edges(ai_settings, aliens)
  aliens.update()
  
  # Look for alien-ship collisions.
  if pygame.sprite.spritecollideany(ship, aliens):
    ship_hit(ai_settings, stats, screen, ship, aliens, bullets)

def ship_hit(ai_settings, stats, screen, ship, aliens, bullets):
  """ respond to ship being hit by alien """
  # Decrement ships left
  stats.ships_left -= 1

  # empty the aliens and bullets groups
  aliens.empty()
  bullets.empty()    

  # create a new fleet and center
  create_fleet(ai_settings, screen, ship, aliens)
  ship.center_ship()

  #pause
  sleep(0.5)
