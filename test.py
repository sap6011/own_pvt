import random

# Example enemy dictionary (this will be replaced during testing)
enemies = {
    1: {"ID": 1, "name": "Creeper", "health": 8, "attack": 3, "experience": 5, "gold": 3},
    2: {"ID": 2, "name": "Wolf", "health": 12, "attack": 4, "experience": 8, "gold": 5},
    3: {"ID": 3, "name": "Bee", "health": 6, "attack": 2, "experience": 4, "gold": 2},
    4: {"ID": 4, "name": "Skeleton", "health": 10, "attack": 4, "experience": 7, "gold": 4}
}


def get_menu_choice(prompt: str, options: list[str]) -> str:
    """Prompt the user until they enter a valid choice (case-insensitive)."""
    options_lower = [opt.lower() for opt in options]
    while True:
        choice = input(prompt).strip().lower()
        if choice in options_lower:
            return choice
        else:
            print(f"Invalid choice. Please choose from {options}.")


def combat_encounter(state: dict, enemy_id: int) -> dict:
    """Simulates a combat encounter between the player and an enemy."""

    enemy = enemies[enemy_id].copy()  # copy so original dict is unchanged
    player = state

    # Apply weapon boosts
    boost_items = ["Rusty Sword", "Iron Dagger", "Magic Scroll"]
    attack_boost = 0
    for item in player["inventory"]:
        if item in boost_items:
            print(f"{item} boosts your attack!")
            attack_boost += 2

    boosted_attack = player["attack"] + attack_boost

    # Track if it's the player's first action
    first_action = True

    while player["health"] > 0 and enemy["health"] > 0:
        print(f"\n{player['name']} HP: {player['health']}/{player['max_health']} | "
              f"{enemy['name']} HP: {enemy['health']}")

        choice = get_menu_choice("Choose [A]ttack, [D]efend, [R]un: ", ["A", "D", "R"])

        # --- Attack ---
        if choice == "a":
            dmg = boosted_attack
            # Double damage if health <= 50%
            if player["health"] <= player["max_health"] // 2:
                dmg *= 2
            enemy["health"] -= dmg
            print(f"{player['name']} attacks {enemy['name']} for {dmg} damage!")

            if enemy["health"] <= 0:
                break

            # Enemy counterattacks
            dmg_taken = random.randint(1, enemy["attack"])
            player["health"] = max(0, player["health"] - dmg_taken)
            print(f"{enemy['name']} hits back for {dmg_taken} damage!")

        # --- Defend ---
        elif choice == "d":
            dmg_taken = random.randint(1, enemy["attack"])
            reduced = max(1, dmg_taken // 2)
            player["health"] = max(0, player["health"] - reduced)
            print(f"{player['name']} defends! Incoming damage reduced to {reduced}.")

        # --- Run ---
        elif choice == "r":
            if first_action:
                print(f"{player['name']} successfully escaped!")
                return player
            else:
                print("Escape failed!")
                dmg_taken = random.randint(1, enemy["attack"])
                player["health"] = max(0, player["health"] - dmg_taken)
                print(f"{enemy['name']} strikes while you try to run! You take {dmg_taken} damage.")

        first_action = False

    # --- After battle ---
    if player["health"] > 0 and enemy["health"] <= 0:
        print(f"\n{player['name']} defeated the {enemy['name']}!")
        print(f"Gained {enemy['experience']} XP and {enemy['gold']} gold.")

        player["experience"] += enemy["experience"]
        player["gold"] += enemy["gold"]
        player["enemies_defeated"] += 1

        # Heal 5 HP, cap at max
        player["health"] = min(player["max_health"], player["health"] + 5)

    elif player["health"] <= 0:
        print(f"\n{player['name']} was defeated by the {enemy['name']}...")

    return player
