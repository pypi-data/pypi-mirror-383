import numpy as np
import pygame
import sys
import time
import argparse
import pkg_resources
from .game.flappy_bird import FlappyBirdEnv
import matplotlib.pyplot as plt

def discretize_state(state):
    bird_y, pipe_x, pipe_height = state
    bird_y_bin = min(int(bird_y // 20), 29)
    pipe_x_bin = max(0, min(int(pipe_x // 50), 23))
    pipe_height_bin = min(int((pipe_height - 100) // 20), 14)
    return (bird_y_bin, pipe_x_bin, pipe_height_bin)

def countdownUser(env):
    env.reset()
    for i in range(3, 0, -1):
        env.WIN.blit(env.BACKGROUND, (0, 0))
        countdown_text = env.font.render(f"Your turn first. Press 'SpaceBar' to fly. Get Ready: {i}", True, env.GOLD, (50, 50, 50))
        env.WIN.blit(countdown_text, (env.WIDTH // 2 - 250, env.HEIGHT // 2 - 10))
        pygame.display.update()
        time.sleep(1)

def countdownAgent(env):
    env.reset()
    for i in range(3, 0, -1):
        env.WIN.blit(env.BACKGROUND, (0, 0))
        countdown_text = env.font.render(f"Agent's turn. Get Ready: {i}", True, env.GOLD, (50, 50, 50))
        env.WIN.blit(countdown_text, (env.WIDTH // 2 - 150, env.HEIGHT // 2 - 10))
        pygame.display.update()
        time.sleep(1)

def play_round(env, q_table, round_num):
    # User plays
    print(f"\nRound {round_num} - User's turn...")
    countdownUser(env)
    state = env.reset()
    done = False
    user_score = 0
    while not done:
        action = 0  # Default: do not jump
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                env.close()
                return False, False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                action = 1
        state, reward, done = env.step(action)
        env.render()
        if reward > 0:
            user_score = env.score

    # Agent plays
    print(f"Round {round_num} - Agent's turn...")
    countdownAgent(env)
    state = env.reset()
    done = False
    agent_score = 0
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                env.close()
                return False, False
        discrete_state = discretize_state(state)
        action = np.argmax(q_table[discrete_state])
        state, reward, done = env.step(action)
        env.render()
        if reward > 0:
            agent_score = env.score

    print(f"Round {round_num} - User Score: {user_score}, Agent Score: {agent_score}")
    winner = "User" if user_score > agent_score else "Agent" if agent_score > user_score else "Tie"
    print(f"Round {round_num} - Winner: {winner}")

    env.WIN.blit(env.BACKGROUND, (0, 0))
    result_text = env.font.render(f"User: {user_score} vs Agent: {agent_score}", True, env.GOLD, (50, 50, 50))
    winner_text = env.font.render(f"Winner: {winner}", True, env.GOLD)
    env.WIN.blit(result_text, (env.WIDTH // 2 - 150, env.HEIGHT // 2 - 40))
    env.WIN.blit(winner_text, (env.WIDTH // 2 - 100, env.HEIGHT // 2 + 10))
    pygame.display.update()
    time.sleep(3)

    return user_score, agent_score

def main():
    parser = argparse.ArgumentParser(description="FlappyAlpha: Human vs. Reinforcement Learning Agent.")
    parser.add_argument('--mode', type=str, choices=['beginner', 'hard'], default='beginner',
                        help='Choose the difficulty for the agent (beginner or hard).')
    args = parser.parse_args()

    print(f"Starting Flappy Bird Challenge ({args.mode.upper()} MODE)...")

    model_filename = f"models/best_q_table_{args.mode}.npy"
    try:
        q_table_path = pkg_resources.resource_filename('flappy_rl', model_filename)
        best_Q_table = np.load(q_table_path)
        print(f"Loaded {model_filename} for Agent")
    except FileNotFoundError:
        print(f"Error: Could not find the model file {model_filename}.")
        print("Please ensure the package was installed correctly and the model files are included.")
        sys.exit(1)

    env = FlappyBirdEnv()
    user_scores = []
    agent_scores = []
    round_num = 1

    while True:
        user_score, agent_score = play_round(env, best_Q_table, round_num)
        if user_score is False:
            break
        user_scores.append(user_score)
        agent_scores.append(agent_score)
        round_num += 1

        env.WIN.blit(env.BACKGROUND, (0, 0))
        continue_text = env.font.render("Press 'c' to continue, 'q' to quit", True, env.GOLD, (50, 50, 50))
        env.WIN.blit(continue_text, (env.WIDTH // 2 - 150, env.HEIGHT // 2))
        pygame.display.update()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        waiting = False
                    elif event.key == pygame.K_q:
                        waiting = False
                        pygame.quit()
                        sys.exit()
    
    if user_scores:
        avg_user_score = np.mean(user_scores)
        avg_agent_score = np.mean(agent_scores)
        print(f"\nAnalysis:")
        print(f"Total Rounds: {len(user_scores)}")
        print(f"Average User Score: {avg_user_score:.2f}")
        print(f"Average Agent Score: {avg_agent_score:.2f}")

        plt.figure(figsize=(10, 6))
        plt.plot(range(1, len(user_scores) + 1), user_scores, marker='o', linestyle='-', color='b', label='User Score')
        plt.plot(range(1, len(agent_scores) + 1), agent_scores, marker='o', linestyle='-', color='g', label='Agent Score')
        plt.xlabel('Round')
        plt.ylabel('Score')
        plt.title(f'User vs Agent Performance ({args.mode.capitalize()} Mode)')
        plt.legend()
        plt.grid(True)
        # Note: Saving files from an installed package should be done in a user-writable directory.
        # For simplicity, we are not saving the plot here.
        plt.show()

    pygame.quit()

if __name__ == "__main__":
    main()
