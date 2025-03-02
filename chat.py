import os
import sys
import time
import shutil
import asyncio

# Tentativa de importar colorama com tratamento de erro
try:
    from colorama import Fore, Style, init
    init()  # Inicializa o colorama
    COLORAMA_AVAILABLE = True
except ImportError:
    print("Aviso: Módulo colorama não encontrado. As cores no terminal não estarão disponíveis.")
    # Definindo classes vazias para substituir as funcionalidades do colorama
    class DummyColor:
        def __getattr__(self, name):
            return ""
    
    Fore = Style = DummyColor()
    COLORAMA_AVAILABLE = False

from app.chat.chat_manager import ChatManager
from app.vector_store.pinecone_store import PineconeManager
from app.vector_store.embeddings import EmbeddingGenerator
from app.chat.conversation_store import ConversationStore
from app.core.logging import logger, log_with_context
from app.core.config import settings

def clear_screen():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Imprime o cabeçalho do sistema"""
    terminal_width = shutil.get_terminal_size().columns
    print(Fore.CYAN + "=" * terminal_width + Style.RESET_ALL)
    print(Fore.GREEN + "Sistema de Gestão de Documentos RAG".center(terminal_width) + Style.RESET_ALL)
    print(Fore.CYAN + "=" * terminal_width + Style.RESET_ALL)
    print(Fore.YELLOW + "Digite suas perguntas ou 'ajuda' para ver os comandos disponíveis." + Style.RESET_ALL)
    print(Fore.CYAN + "-" * terminal_width + Style.RESET_ALL)

def print_help():
    """Imprime a ajuda do sistema"""
    print(Fore.GREEN + "\nComandos disponíveis:" + Style.RESET_ALL)
    print(Fore.YELLOW + "  ajuda       " + Style.RESET_ALL + "- Exibe esta mensagem de ajuda")
    print(Fore.YELLOW + "  limpar      " + Style.RESET_ALL + "- Limpa a tela")
    print(Fore.YELLOW + "  id          " + Style.RESET_ALL + "- Mostra o ID da conversa atual")
    print(Fore.YELLOW + "  nova        " + Style.RESET_ALL + "- Inicia uma nova conversa")
    print(Fore.YELLOW + "  carregar ID " + Style.RESET_ALL + "- Carrega uma conversa existente pelo ID")
    print(Fore.YELLOW + "  histórico   " + Style.RESET_ALL + "- Mostra o histórico da conversa atual")
    print(Fore.YELLOW + "  sair        " + Style.RESET_ALL + "- Sai do sistema")
    print()

def initialize_components():
    """Inicializa os componentes necessários para o chat"""
    try:
        log_with_context("info", "Inicializando banco de dados")
        conversation_store = ConversationStore()
        log_with_context("info", "Banco de dados inicializado com sucesso")
        
        log_with_context("info", "Inicializando PineconeManager")
        pinecone_manager = PineconeManager(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT,
            index_name=settings.PINECONE_INDEX_NAME
        )
        
        log_with_context("info", "Inicializando EmbeddingGenerator")
        embedding_generator = EmbeddingGenerator(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_EMBEDDING_MODEL
        )
        
        log_with_context("info", "Inicializando ChatManager")
        chat_manager = ChatManager(
            pinecone_manager=pinecone_manager,
            embedding_generator=embedding_generator,
            conversation_store=conversation_store,
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL
        )
        
        log_with_context("info", "Componentes inicializados com sucesso")
        return chat_manager, conversation_store
    except Exception as e:
        log_with_context("error", f"Erro ao inicializar componentes: {str(e)}", exception=e)
        print(Fore.RED + f"Erro ao inicializar componentes: {str(e)}" + Style.RESET_ALL)
        sys.exit(1)

def display_message(role, content):
    """Exibe uma mensagem formatada no terminal"""
    if role == "user":
        print(Fore.GREEN + "Você: " + Style.RESET_ALL + content)
    elif role == "assistant":
        print(Fore.BLUE + "Assistente: " + Style.RESET_ALL + content)
    elif role == "system":
        print(Fore.YELLOW + "Sistema: " + Style.RESET_ALL + content)

def display_sources(sources):
    """Exibe as fontes de informação utilizadas na resposta"""
    if sources and len(sources) > 0:
        print(Fore.CYAN + "\nFontes utilizadas:" + Style.RESET_ALL)
        for i, source in enumerate(sources, 1):
            print(f"{i}. {source['title']} (página {source.get('page', 'N/A')})")
        print()

async def main_async():
    """Função principal assíncrona do sistema de chat"""
    clear_screen()
    print_header()
    
    # Inicializa os componentes
    chat_manager, conversation_store = initialize_components()
    
    # Cria uma nova conversa
    conversation = chat_manager.create_conversation()
    conversation_id = conversation.conversation_id
    log_with_context("info", "Nova conversa criada", {"conversation_id": conversation_id})
    
    # Loop principal
    while True:
        try:
            # Solicita entrada do usuário
            user_input = input(Fore.GREEN + "Você: " + Style.RESET_ALL)
            
            # Processa comandos especiais
            if user_input.lower() == "sair":
                log_with_context("info", "Usuário encerrou o chat", {"conversation_id": conversation_id})
                print(Fore.YELLOW + "Encerrando chat. Até logo!" + Style.RESET_ALL)
                break
                
            elif user_input.lower() == "ajuda":
                print_help()
                continue
                
            elif user_input.lower() == "limpar":
                clear_screen()
                print_header()
                continue
                
            elif user_input.lower() == "id":
                print(Fore.YELLOW + f"ID da conversa atual: {conversation_id}" + Style.RESET_ALL)
                continue
                
            elif user_input.lower() == "nova":
                conversation = chat_manager.create_conversation()
                conversation_id = conversation.conversation_id
                log_with_context("info", "Nova conversa criada", {"conversation_id": conversation_id})
                print(Fore.YELLOW + f"Nova conversa iniciada. ID: {conversation_id}" + Style.RESET_ALL)
                continue
                
            elif user_input.lower().startswith("carregar "):
                try:
                    load_id = user_input.split(" ", 1)[1].strip()
                    conversation = conversation_store.get_conversation(load_id)
                    if conversation:
                        conversation_id = load_id
                        log_with_context("info", f"Conversa carregada: {load_id}", {"conversation_id": load_id})
                        print(Fore.YELLOW + f"Conversa carregada com sucesso. ID: {load_id}" + Style.RESET_ALL)
                        
                        # Exibe o histórico da conversa carregada
                        messages = conversation.messages
                        print(Fore.CYAN + "\nHistórico da conversa:" + Style.RESET_ALL)
                        for msg in messages:
                            display_message(msg["role"], msg["content"])
                        print()
                    else:
                        print(Fore.RED + f"Conversa com ID {load_id} não encontrada." + Style.RESET_ALL)
                except Exception as e:
                    log_with_context("error", f"Erro ao carregar conversa: {str(e)}", 
                                    {"conversation_id": conversation_id}, exception=e)
                    print(Fore.RED + f"Erro ao carregar conversa: {str(e)}" + Style.RESET_ALL)
                continue
                
            elif user_input.lower() == "histórico":
                try:
                    conversation = conversation_store.get_conversation(conversation_id)
                    if conversation:
                        messages = conversation.messages
                        print(Fore.CYAN + "\nHistórico da conversa:" + Style.RESET_ALL)
                        for msg in messages:
                            display_message(msg["role"], msg["content"])
                        print()
                    else:
                        print(Fore.RED + "Histórico não disponível." + Style.RESET_ALL)
                except Exception as e:
                    log_with_context("error", f"Erro ao exibir histórico: {str(e)}", 
                                    {"conversation_id": conversation_id}, exception=e)
                    print(Fore.RED + f"Erro ao exibir histórico: {str(e)}" + Style.RESET_ALL)
                continue
                
            # Processa a mensagem do usuário
            if user_input.strip():
                log_with_context("info", f"Mensagem do usuário: {user_input}", {"conversation_id": conversation_id})
                
                # Exibe indicador de processamento
                print(Fore.BLUE + "Assistente: " + Style.RESET_ALL, end="", flush=True)
                
                try:
                    # Obtém resposta do assistente (agora usando await)
                    start_time = time.time()
                    response = await chat_manager.send_message(conversation_id, user_input)
                    end_time = time.time()
                    
                    # Limpa a linha atual
                    print("\r" + " " * shutil.get_terminal_size().columns, end="\r")
                    
                    # Exibe a resposta
                    print(Fore.BLUE + "Assistente: " + Style.RESET_ALL + response["content"])
                    
                    # Exibe as fontes, se disponíveis
                    if "sources" in response and response["sources"]:
                        display_sources(response["sources"])
                    
                    # Registra métricas
                    processing_time = end_time - start_time
                    log_with_context("info", f"Resposta gerada em {processing_time:.2f}s", 
                                    {"conversation_id": conversation_id, "processing_time": processing_time})
                    
                except Exception as e:
                    # Limpa a linha atual
                    print("\r" + " " * shutil.get_terminal_size().columns, end="\r")
                    
                    log_with_context("error", f"Erro ao processar mensagem: {str(e)}", 
                                    {"conversation_id": conversation_id}, exception=e)
                    print(Fore.RED + f"Erro ao processar mensagem: {str(e)}" + Style.RESET_ALL)
            
        except KeyboardInterrupt:
            log_with_context("info", "Interrupção do usuário detectada", {"conversation_id": conversation_id})
            print(Fore.YELLOW + "\nEncerrando chat. Até logo!" + Style.RESET_ALL)
            break
            
        except Exception as e:
            log_with_context("error", f"Erro inesperado: {str(e)}", {"conversation_id": conversation_id}, exception=e)
            print(Fore.RED + f"Erro inesperado: {str(e)}" + Style.RESET_ALL)

def main():
    """Função principal do sistema de chat"""
    asyncio.run(main_async())

if __name__ == "__main__":
    main() 