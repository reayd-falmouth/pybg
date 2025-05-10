import pygame

# Events
EVENT_GAME = pygame.USEREVENT + 1


def post_game_event(event_type: str, **kwargs):
    pygame.event.post(
        pygame.event.Event(EVENT_GAME, {"event_type": event_type, **kwargs})
    )
