#!/usr/bin/env python3
"""
Loudly API SDK Test Script
Tests all major functionality of the Loudly API client with separate functions for each API call.
"""

from loudly import LoudlyClient, LoudlyAPIError


def test_genres(sdk: LoudlyClient) -> None:
    """Test listing available genres."""
    print("\n=== GENRES ===")
    try:
        genres = sdk.list_genres()
        print(f"Found {len(genres)} genres:")
        for genre in genres:
            print(f"   {genre['id']}: {genre['name']} ({genre['description']})")
    except LoudlyAPIError as e:
        print(f"Genres API Error [{e.status_code}]: {e.message}")
    except Exception as e:
        print(f"Genres Error: {e}")


def test_structures(sdk: LoudlyClient) -> None:
    """Test listing available song structures."""
    print("\n=== STRUCTURES ===")
    try:
        structures = sdk.list_structures()
        print(f" Found {len(structures)} structures:")
        for s in structures:
            print(f"   {s['id']}: {s['name']} ({s['description']})")
    except LoudlyAPIError as e:
        print(f"Structures API Error [{e.status_code}]: {e.message}")
    except Exception as e:
        print(f"Structures Error: {e}")


def test_random_prompt(sdk: LoudlyClient) -> None:
    """Test getting a random prompt."""
    print("\n=== RANDOM PROMPT ===")
    try:
        prompt_data = sdk.get_random_prompt()
        print(f"Random prompt: {prompt_data['prompt']}")
    except LoudlyAPIError as e:
        print(f"Random Prompt API Error [{e.status_code}]: {e.message}")
    except Exception as e:
        print(f"Random Prompt Error: {e}")


def test_song_tags(sdk: LoudlyClient) -> None:
    """Test getting song tags with filters."""
    print("\n=== SONG TAGS ===")
    try:
        tags = sdk.get_song_tags(
            mood=["Dreamy", "Laid Back", "Dark"],
            genre=["Funk", "Beats", "Indian"],
            key=["E Major", "Ab/G# Major"]
        )
        print("Song tags retrieved:")
        print(f"Filters used: mood=['Dreamy', 'Laid Back', 'Dark'], genre=['Funk', 'Beats', 'Indian'], key=['E Major', 'Ab/G# Major']")
        print(f"Result: {tags}")
    except LoudlyAPIError as e:
        print(f"Song Tags API Error [{e.status_code}]: {e.message}")
    except Exception as e:
        print(f"Song Tags Error: {e}")


def test_list_songs(sdk: LoudlyClient) -> None:
    """Test listing songs with pagination."""
    print("\n=== SONGS LIST ===")
    try:
        songs_data = sdk.list_songs(page=1, per_page=10)
        print(f"Found {len(songs_data['items'])} songs on page 1:")
        for song in songs_data["items"]:
            print(f"   {song['id']}: {song['title']} ({song['duration']} sec)")
    except LoudlyAPIError as e:
        print(f"List Songs API Error [{e.status_code}]: {e.message}")
    except Exception as e:
        print(f"List Songs Error: {e}")


def test_generate_ai_song(sdk: LoudlyClient) -> None:
    """Test AI song generation with parameters."""
    print("\n=== AI SONG GENERATION ===")
    try:
        song = sdk.generate_ai_song(
            genre="House",
            duration=30,
            energy="high",
            bpm=115,
            key_root="D",
            key_quality="minor",
            instruments="Synth,Drums",
            test=True
        )
        
        print("AI Song generated successfully:")
        print(f"Title: {song['title']}")
        print(f"Music File: {song['music_file_path']}")
        print(f"Duration: {song.get('duration', 'N/A')} ms")
        print(f"BPM: {song.get('bpm', 'N/A')}")
        print(f"Key: {song.get('key', {}).get('name', 'N/A')}")
        
    except LoudlyAPIError as e:
        print(f"AI Song Generation API Error [{e.status_code}]: {e.message}")
    except Exception as e:
        print(f"AI Song Generation Error: {e}")


def test_generate_song_from_prompt(sdk: LoudlyClient) -> None:
    """Test song generation from text prompt."""
    print("\n=== SONG FROM PROMPT ===")
    try:
        song_from_prompt = sdk.generate_song_from_prompt(
            prompt="A 90-second energetic house track with tropical vibes and a melodic flute line",
            duration=30,
            test=True
        )
        
        print("Song from prompt generated successfully:")
        print(f"Prompt: 'A 90-second energetic house track with tropical vibes and a melodic flute line'")
        print(f"Title: {song_from_prompt['title']}")
        print(f"Music File: {song_from_prompt['music_file_path']}")
        print(f"Duration: {song_from_prompt['duration']} ms")
        print(f"BPM: {song_from_prompt['bpm']}")
        print(f"Key: {song_from_prompt['key']['name']}")
        
    except LoudlyAPIError as e:
        print(f"Song from Prompt API Error [{e.status_code}]: {e.message}")
    except Exception as e:
        print(f"Song from Prompt Error: {e}")


def test_account_limits(sdk: LoudlyClient) -> None:
    """Test getting account limits information."""
    print("\n=== ACCOUNT LIMITS ===")
    try:
        # Test without date filters
        print("Getting current limits...")
        limits = sdk.get_limits()
        print("Current limits retrieved:")
        for limit in limits.get('limits', []):
            print(f"{limit['request_type']}: {limit['used']}/{limit['limit']} ({limit['left']} remaining)")
        
        top_up = limits.get('top_up', {})
        if top_up.get('total', 0) > 0:
            print(f"Top-up available: {top_up['available']}/{top_up['total']}")
        
        # Test with date range
        print("\n Getting limits for specific date range...")
        limits_filtered = sdk.get_limits(date_from="2025-02-25", date_to="2025-03-27")
        print("Filtered limits retrieved:")
        print(f"Date range: 2025-02-25 to 2025-03-27")
        for limit in limits_filtered.get('limits', []):
            print(f"{limit['request_type']}: {limit['used']}/{limit['limit']} ({limit['left']} remaining)")
        
    except LoudlyAPIError as e:
        print(f"Account Limits API Error [{e.status_code}]: {e.message}")
    except Exception as e:
        print(f"Account Limits Error: {e}")


def main():
    """Main function to run all tests."""
    print("Loudly API SDK Test Suite")
    print("=" * 60)
    
    # Initialize SDK
    sdk = LoudlyClient(
        api_key="gkatOxIWWGY26B4Czb9H8UF01JGwHa2Kiigf8nTiHnI", 
        base_url="https://soundtracks.loudly.com"
    )
    
    # Run all tests
    test_functions = [
        test_genres,
        test_structures,
        test_random_prompt,
        test_song_tags,
        test_list_songs,
        test_generate_ai_song,
        test_generate_song_from_prompt,
        test_account_limits
    ]
    
    for test_func in test_functions:
        try:
            test_func(sdk)
        except KeyboardInterrupt:
            print("\n Test interrupted by user")
            break
        except Exception as e:
            print(f"Unexpected error in {test_func.__name__}: {e}")
    
    print("\n" + "=" * 60)
    print("Test suite completed")


if __name__ == "__main__":
    main()