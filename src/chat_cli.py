import asyncio
from src.agent.chat_agent import AnnieMacAgent
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.models.database import Artist, DATABASE_URL

async def list_artists():
    engine = create_engine(DATABASE_URL)
    with Session(engine) as session:
        artists = session.query(Artist).all()
        print("\nAvailable artists:")
        for artist in artists:
            print(f"- {artist.name}")

async def interactive_chat():
    print("\n=== Annie Mac Music Chat ===")
    print("Welcome! Let's talk about music. I know quite a bit about Disclosure, Bicep, and Fred Again.")
    print("\nCommands:")
    print("- Type 'exit' or 'quit' to end the chat")
    print("- Type 'clear' to clear the screen")
    print("- Type 'artists' to see available artists")
    print("- Press Ctrl+C to force quit")
    print("\nExample questions:")
    print("- 'What do you think about Disclosure?'")
    print("- 'Tell me about Fred Again'")
    print("- 'I've been listening to Bicep lately'")
    print("\n" + "="*30 + "\n")
    
    agent = AnnieMacAgent()
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("\nAnnie: Thanks for the chat! Keep the music playing! x")
                break
            
            if user_input.lower() == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                continue
            
            if user_input.lower() == 'artists':
                await list_artists()
                continue
                
            if user_input:
                response = await agent.chat(user_input)
                print(f"\nAnnie: {response}")
            
        except KeyboardInterrupt:
            print("\n\nAnnie: Catch you later! Keep dancing! x")
            break
        except Exception as e:
            print(f"\nOops! Something went wrong: {str(e)}")
            print("Let's try again!")

if __name__ == "__main__":
    asyncio.run(interactive_chat()) 