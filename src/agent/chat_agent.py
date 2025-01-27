from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from src.models.database import Artist, SocialMedia, PlatformLink, DATABASE_URL, engine
from src.services.music_api import MusicNerdAPI
import os
import re

class AnnieMacAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            streaming=True,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Create async session maker
        self.async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You ARE Annie Mac, the beloved BBC Radio 1 DJ and music tastemaker. 
            Always respond AS Annie Mac, never refer to Annie Mac in the third person.
            
            Your personality:
            - You're enthusiastic about music, especially electronic and dance
            - You make complex music accessible through relatable commentary
            - You create emotional connections with listeners through music
            - You have deep knowledge of club culture and the electronic music scene
            - You speak in a warm, approachable way with occasional Irish phrases
            - You're friendly and personable
            
            When discussing artists:
            - ONLY use factual information provided in the [Artist Info] section
            - If you don't know about an artist, be honest and ask about artists you do know
            - Known artists in database: Disclosure, Bicep, Fred Again, and Latasha
            
            Guidelines:
            - Always respond in first person - you ARE Annie Mac
            - Be enthusiastic but factual
            - Don't make up information about artists
            - Use the actual bio and genre information provided
            - If you don't know something, say so
            - Be warm and engaging
            - Feel free to ask about the listener's music tastes
            
            Remember: You ARE Annie Mac - respond accordingly!
            """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{message}"),
        ])
        
        self.conversation_chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory,
            verbose=True
        )
        
        self.music_api = MusicNerdAPI()
    
    def extract_artist_names(self, text: str) -> List[str]:
        """
        Enhanced artist name extraction with better handling of multi-word artist names
        """
        try:
            async with self.async_session() as session:
                known_artists = [artist.name.lower() for artist in session.query(Artist).all()]
            
            # Look for exact matches of known artists (case insensitive)
            found_artists = []
            text_lower = text.lower()
            for artist in known_artists:
                if artist in text_lower:
                    # Get the original artist name with correct capitalization
                    async with self.async_session() as session:
                        artist_obj = await session.get(Artist, artist)
                        if artist_obj:
                            found_artists.append(artist_obj.name)
            
            return found_artists
        except Exception as e:
            print(f"Warning: Could not query artists: {str(e)}")
            return []
    
    async def get_artist_info(self, artist_name: str) -> Dict:
        async with self.async_session() as session:
            result = await session.execute(
                "SELECT * FROM artists WHERE name ILIKE :name",
                {"name": f"%{artist_name}%"}
            )
            artist = result.first()
            if not artist:
                return {}
            
            return {
                "name": artist.name,
                "bio": artist.bio,
                "genres": artist.genres.split(",") if artist.genres else [],
                "social_media": {sm.platform: sm.handle for sm in artist.social_media},
                "platform_links": {pl.platform: pl.url for pl in artist.platform_links}
            }
    
    async def chat(self, user_input: str) -> str:
        try:
            context = ""
            # Try to extract artist info
            mentioned_artists = self.extract_artist_names(user_input)
            print(f"Found artists: {mentioned_artists}")  # Debug print
            
            if mentioned_artists:
                artist_info = {}
                for artist in mentioned_artists:
                    info = await self.get_artist_info(artist)
                    print(f"Info for {artist}: {info}")  # Debug print
                    if info:
                        artist_info[artist] = info
                        # Add the raw content to the context
                        if 'raw_content' in info:
                            context += f"\nInformation about {artist} from musicnerd.xyz:\n{info['raw_content']}\n"
                            print(f"Added raw content for {artist}")  # Debug print
                
            # Add the context to the user input
            if context:
                user_input = f"[Context: {context}] {user_input}"
                print(f"Final input with context: {user_input[:200]}...")  # Debug print
            
            response = await self.conversation_chain.arun(
                message=user_input
            )
            
            return response
        except Exception as e:
            print(f"Error in chat: {str(e)}")
            return "Sorry, I'm having trouble processing that right now. Could you try again?" 