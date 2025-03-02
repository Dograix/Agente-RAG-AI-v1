import os
import sys
import json
import asyncio
import argparse
from datetime import datetime
from app.chat.conversation_store import ConversationStore
from app.core.logging import logger

def format_timestamp(timestamp_str):
    """Formata um timestamp ISO para exibição amigável"""
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except:
        return timestamp_str

def list_conversations(store, limit=10, offset=0):
    """Lista as conversas disponíveis"""
    conversations = store.list_conversations(limit=limit, offset=offset)
    
    if not conversations:
        print("\nNenhuma conversa encontrada.")
        return
    
    print("\n📋 Conversas Disponíveis:")
    print("-" * 120)
    print(f"{'ID':<36} {'Título':<30} {'Data':<20} {'Mensagens':<10} {'Última Atualização':<20}")
    print("-" * 120)
    
    for conv in conversations:
        title = conv.get("metadata", {}).get("title", "Sem título")
        created_at = format_timestamp(conv.get("created_at", "N/A"))
        updated_at = format_timestamp(conv.get("updated_at", "N/A"))
        message_count = conv.get("message_count", 0)
        
        print(f"{conv['conversation_id']:<36} {title[:30]:<30} {created_at:<20} {message_count:<10} {updated_at:<20}")
    
    print("-" * 120)
    total = len(store.list_conversations(limit=0))
    print(f"Exibindo {len(conversations)} de {total} conversas")

def view_conversation(store, conversation_id):
    """Exibe o conteúdo de uma conversa"""
    conversation = store.get_conversation(conversation_id)
    
    if not conversation:
        print(f"\n❌ Conversa com ID {conversation_id} não encontrada.")
        return
    
    title = conversation.metadata.get("title", "Sem título")
    created_at = format_timestamp(conversation.created_at)
    
    print(f"\n📝 Conversa: {title}")
    print(f"ID: {conversation.conversation_id}")
    print(f"Data de criação: {created_at}")
    print("-" * 100)
    
    # Exibe as mensagens (exceto a do sistema)
    for msg in conversation.messages:
        if msg["role"] == "system":
            continue
            
        timestamp = format_timestamp(msg.get("timestamp", "N/A"))
        role_emoji = "👤" if msg["role"] == "user" else "🤖"
        role_name = "Você" if msg["role"] == "user" else "Assistente"
        
        print(f"\n{role_emoji} {role_name} ({timestamp}):")
        print(f"{msg['content']}")
        
        # Se for resposta do assistente e tiver metadados de contexto
        if msg["role"] == "assistant" and msg.get("metadata"):
            metadata = msg["metadata"]
            if "context_source" in metadata:
                source = metadata["context_source"]
                source_name = source.split("/")[-1] if "/" in source else source
                score = metadata.get("similarity_score", 0)
                print(f"\n📚 Fonte: {source_name} (Relevância: {score:.2f})")
        
        print("-" * 100)

def delete_conversation(store, conversation_id):
    """Exclui uma conversa"""
    # Primeiro verifica se a conversa existe
    conversation = store.get_conversation(conversation_id)
    
    if not conversation:
        print(f"\n❌ Conversa com ID {conversation_id} não encontrada.")
        return
    
    # Pede confirmação
    title = conversation.metadata.get("title", "Sem título")
    print(f"\n⚠️ Tem certeza que deseja excluir a conversa '{title}'?")
    print(f"ID: {conversation_id}")
    confirmation = input("Digite 'CONFIRMAR' para prosseguir: ")
    
    if confirmation != "CONFIRMAR":
        print("Operação cancelada.")
        return
    
    # Exclui a conversa
    if store.delete_conversation(conversation_id):
        print(f"\n✅ Conversa '{title}' excluída com sucesso!")
    else:
        print(f"\n❌ Erro ao excluir a conversa.")

def export_conversation(store, conversation_id, output_file=None):
    """Exporta uma conversa para um arquivo JSON"""
    conversation = store.get_conversation(conversation_id)
    
    if not conversation:
        print(f"\n❌ Conversa com ID {conversation_id} não encontrada.")
        return
    
    # Define o nome do arquivo se não fornecido
    if not output_file:
        title = conversation.metadata.get("title", "conversa")
        title = "".join(c if c.isalnum() else "_" for c in title)
        output_file = f"{title}_{conversation_id[:8]}.json"
    
    # Exporta para JSON
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(conversation.to_dict(), f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Conversa exportada com sucesso para '{output_file}'")
    except Exception as e:
        print(f"\n❌ Erro ao exportar conversa: {str(e)}")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Gerenciador de Conversas")
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")
    
    # Comando list
    list_parser = subparsers.add_parser("list", help="Lista as conversas disponíveis")
    list_parser.add_argument("--limit", type=int, default=10, help="Limite de conversas a exibir")
    list_parser.add_argument("--offset", type=int, default=0, help="Offset para paginação")
    
    # Comando view
    view_parser = subparsers.add_parser("view", help="Exibe o conteúdo de uma conversa")
    view_parser.add_argument("id", help="ID da conversa a visualizar")
    
    # Comando delete
    delete_parser = subparsers.add_parser("delete", help="Exclui uma conversa")
    delete_parser.add_argument("id", help="ID da conversa a excluir")
    
    # Comando export
    export_parser = subparsers.add_parser("export", help="Exporta uma conversa para JSON")
    export_parser.add_argument("id", help="ID da conversa a exportar")
    export_parser.add_argument("--output", help="Caminho do arquivo de saída")
    
    args = parser.parse_args()
    
    # Inicializa o armazenamento de conversas
    store = ConversationStore()
    
    # Executa o comando apropriado
    if args.command == "list":
        list_conversations(store, args.limit, args.offset)
    elif args.command == "view":
        view_conversation(store, args.id)
    elif args.command == "delete":
        delete_conversation(store, args.id)
    elif args.command == "export":
        export_conversation(store, args.id, args.output)
    else:
        # Se nenhum comando for fornecido, mostra a ajuda
        parser.print_help()

if __name__ == "__main__":
    main() 