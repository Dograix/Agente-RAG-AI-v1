from typing import List, Dict, Any, Optional
from datetime import datetime

# Importações diretas sem try/except
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from ..core.config import settings
from ..core.logging import logger
from ..vector_store.pinecone_store import PineconeManager
from ..vector_store.embeddings import EmbeddingGenerator
from .conversation_store import ConversationStore, Conversation
import re

class ChatManager:
    def __init__(
        self,
        pinecone_manager: PineconeManager,
        embedding_generator: EmbeddingGenerator,
        conversation_store: ConversationStore = None,
        api_key: str = None,
        model: str = None,
        user_id: str = "default_user"
    ):
        self.pinecone_manager = pinecone_manager
        self.embedding_generator = embedding_generator
        self.conversation_store = conversation_store or ConversationStore()
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self.user_id = user_id
        
        if not self.api_key:
            raise ValueError("OpenAI API Key não configurada")
        
        self.chat = ChatOpenAI(
            temperature=0.7,
            model=self.model,
            openai_api_key=self.api_key
        )
        
        # Modelo para classificação (temperatura mais baixa para decisões mais consistentes)
        self.classifier = ChatOpenAI(
            temperature=0.1,
            model="gpt-4o-mini",  # Atualizado para o mesmo modelo principal
            openai_api_key=self.api_key
        )
        
        # Thresholds de relevância para o contexto
        self.relevance_thresholds = {
            "high": 0.80,    # Contexto altamente relevante
            "medium": 0.70,  # Contexto moderadamente relevante
            "low": 0.60,     # Contexto com baixa relevância
            "very_low": 0.45 # Contexto com relevância muito baixa
        }
        
        # Threshold mínimo para considerar uma resposta válida
        self.minimum_relevance_threshold = 0.35  # Abaixo disso, o contexto é considerado irrelevante
        
        # Template do sistema melhorado
        self.system_template = """Você é um assistente útil e amigável especializado no Sistema Gestor.
        
        Regras importantes:
        1. Use APENAS as informações do contexto fornecido para responder às perguntas
        2. Se a informação estiver no contexto, forneça uma resposta detalhada e bem estruturada
        3. Se não encontrar a informação específica no contexto, diga claramente que não encontrou
        4. Seja direto e claro em suas respostas
        5. Mantenha o tom profissional mas amigável
        6. Você APENAS pode responder perguntas relacionadas ao Sistema Gestor de Documentos RAG e seus processos
        7. Para perguntas sobre outros sistemas, produtos ou serviços não relacionados, explique que não possui essas informações
        
        Lembre-se: Sua função é ajudar o usuário a entender o Sistema Gestor de Documentos RAG e seus processos, conforme documentado nos arquivos da empresa."""
    
    def create_conversation(self, title: str = None) -> Conversation:
        """Cria uma nova conversa"""
        metadata = {"title": title or f"Conversa {datetime.now().strftime('%Y-%m-%d %H:%M')}"}
        
        # Cria a conversa no armazenamento
        conversation = self.conversation_store.create_conversation(
            user_id=self.user_id,
            metadata=metadata
        )
        
        # Adiciona mensagem do sistema
        self.conversation_store.add_message_to_conversation(
            conversation_id=conversation.conversation_id,
            user_id=self.user_id,
            role="system",
            content=self.system_template
        )
        
        logger.info(
            f"Nova conversa criada",
            extra={
                "conversation_id": conversation.conversation_id,
                "user_id": self.user_id,
                "title": metadata["title"]
            }
        )
        
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Recupera uma conversa pelo ID"""
        return self.conversation_store.get_conversation(
            conversation_id=conversation_id,
            user_id=self.user_id
        )
    
    def list_conversations(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Lista as conversas do usuário atual"""
        return self.conversation_store.list_conversations(
            user_id=self.user_id,
            limit=limit,
            offset=offset
        )
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Exclui uma conversa"""
        return self.conversation_store.delete_conversation(
            conversation_id=conversation_id,
            user_id=self.user_id
        )
    
    async def get_context(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Busca contexto relevante para a query"""
        return await self.pinecone_manager.search(
            embedding_generator=self.embedding_generator,
            query=query,
            top_k=top_k
        )
    
    def _format_context(self, context_results: List[Dict[str, Any]]) -> str:
        """Formata os resultados do contexto em um texto"""
        if not context_results:
            return "Nenhum contexto relevante encontrado."
            
        context_text = "Contexto relevante:\n\n"
        for i, result in enumerate(context_results):
            metadata = result["metadata"]
            source = metadata.get("source", "Fonte desconhecida")
            source_name = source.split("/")[-1] if "/" in source else source
            
            context_text += f"Trecho {i+1} (Fonte: {source_name}):\n"
            # Aqui adicionamos o texto do chunk ao contexto
            context_text += f"{metadata.get('text', '[Texto não disponível]')}\n\n"
        return context_text
    
    def _get_conversation_messages(self, conversation: Conversation) -> List:
        """Converte mensagens da conversa para o formato do LangChain"""
        # Converte para formato do LangChain
        langchain_messages = []
        for msg in conversation.messages:
            if msg["role"] == "system":
                langchain_messages.append(SystemMessage(content=msg["content"]))
            elif msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        
        return langchain_messages
    
    def _format_messages_for_classification(self, messages: List[Dict[str, Any]]) -> str:
        """Formata as mensagens para o prompt de classificação"""
        formatted = []
        for msg in messages:
            if msg["role"] != "system":  # Ignora mensagens do sistema
                role = "Usuário" if msg["role"] == "user" else "Assistente"
                formatted.append(f"{role}: {msg['content']}")
        
        return "\n".join(formatted)
    
    async def _classify_message_intent(self, content: str, conversation: Conversation) -> str:
        """
        Classifica a intenção da mensagem para determinar seu tipo
        
        Returns:
            str: Tipo da mensagem ("SISTEMA", "CONVERSA", "CONHECIMENTO_GERAL")
        """
        # Verificação rápida para saudações simples e comandos básicos
        simple_greetings = ["oi", "olá", "bom dia", "boa tarde", "boa noite", "tudo bem", "como vai"]
        basic_commands = ["sair", "ajuda", "obrigado", "obrigada", "valeu", "tchau"]
        
        # Verifica se a mensagem é uma saudação simples ou comando básico
        if content.lower().strip() in simple_greetings or content.lower().strip() in basic_commands:
            logger.info(f"Classificação rápida: Mensagem simples detectada - CONVERSA")
            return "CONVERSA"
            
        # Obtém as últimas mensagens para contexto
        recent_messages = conversation.messages[-5:] if len(conversation.messages) > 5 else conversation.messages
        
        # Prepara o prompt para classificação
        classification_prompt = f"""
        Determine se a seguinte mensagem requer busca em documentos do sistema para ser respondida adequadamente.
        
        Contexto: Você é um assistente para uma empresa que responde perguntas sobre os sistemas e processos internos.
        
        Você deve classificar a mensagem do usuário em uma das seguintes categorias:
        
        1) SISTEMA: Pergunta ou solicitação relacionada aos sistemas, processos ou regras de negócio da empresa (REQUER BUSCA)
        2) CONVERSA: Saudação, agradecimento, ou mensagem conversacional geral (NÃO REQUER BUSCA)
        3) CONHECIMENTO_GERAL: Pergunta sobre conhecimento geral não relacionado aos sistemas da empresa, como esportes, entretenimento, etc. (NÃO REQUER BUSCA)
        
        Exemplos:
        - "Como faço para acessar o sistema de RH?" -> SISTEMA
        - "Bom dia, como você está?" -> CONVERSA
        - "Quantos títulos tem o São Paulo?" -> CONHECIMENTO_GERAL
        - "Qual o processo para aprovação de férias?" -> SISTEMA
        - "Obrigado pela ajuda!" -> CONVERSA
        - "Quem é o presidente do Brasil?" -> CONHECIMENTO_GERAL
        
        Histórico recente da conversa:
        {self._format_messages_for_classification(recent_messages)}
        
        Mensagem atual do usuário: "{content}"
        
        Responda apenas com "SISTEMA", "CONVERSA" ou "CONHECIMENTO_GERAL":
        """
        
        # Usa o modelo para classificação
        response = await self.classifier.ainvoke([HumanMessage(content=classification_prompt)])
        
        # Analisa a resposta
        response_text = response.content.upper()
        
        if "SISTEMA" in response_text:
            logger.info(f"Classificação da mensagem: SISTEMA - Requer busca")
            return "SISTEMA"
        elif "CONHECIMENTO_GERAL" in response_text:
            logger.info(f"Classificação da mensagem: CONHECIMENTO_GERAL - Não requer busca")
            return "CONHECIMENTO_GERAL"
        else:
            logger.info(f"Classificação da mensagem: CONVERSA - Não requer busca")
            return "CONVERSA"
    
    def _evaluate_context_relevance(self, context_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Avalia a relevância do contexto encontrado
        
        Returns:
            Dict com informações sobre a relevância do contexto
        """
        if not context_results or len(context_results) == 0:
            return {
                "is_relevant": False,
                "relevance_level": "none",
                "response_type": "clarification",
                "best_score": 0.0
            }
        
        # Obtém o score do melhor resultado
        best_match_score = context_results[0]["score"]
        original_score = best_match_score  # Guarda o score original para logging
        
        # Verifica se o texto do contexto contém informações relevantes
        context_text = context_results[0]["metadata"].get("text", "").lower()
        
        # Lista de palavras-chave que indicam conteúdo não relacionado ao sistema
        non_system_keywords = [
            # Esportes
            "futebol", "campeonato", "time de futebol", "jogo de futebol", "partida de futebol", 
            "gol", "copa do mundo", "libertadores", "brasileiro", "mundial de clubes", 
            "jogador de futebol", "atleta", "torcedor", "estádio", "arena", "bola", 
            "técnico de futebol", "treinador de futebol",
            
            # Entretenimento
            "filme", "cinema", "série de tv", "ator", "atriz", "música", "cantor", "cantora",
            "show", "concerto", "teatro", "novela", "programa de tv", "televisão",
            
            # Política e geografia
            "presidente do", "governador", "prefeito", "ministro", "senador", "deputado",
            "país", "capital do", "continente", "oceano", "montanha",
            
            # Outros temas gerais
            "receita de", "comida", "restaurante", "viagem", "hotel", "turismo",
            "animal", "planta", "história mundial", "guerra mundial", "religião",
            
            # Compras e produtos não relacionados
            "camisa", "roupa", "comprar", "loja online", "produto", "preço", "pagamento",
            "cartão de crédito", "boleto", "frete", "entrega", "devolução", "troca"
        ]
        
        # Verifica se o contexto contém palavras-chave não relacionadas ao sistema
        # Usa uma abordagem mais precisa para evitar falsos positivos
        non_system_words = []
        for keyword in non_system_keywords:
            # Verifica se a palavra-chave está presente como uma palavra completa
            # usando expressões regulares com limites de palavra
            if re.search(r'\b' + re.escape(keyword) + r'\b', context_text):
                non_system_words.append(keyword)
        
        contains_non_system_content = len(non_system_words) > 0
        
        # Se o contexto contém palavras-chave não relacionadas ao sistema, reduz o score
        if contains_non_system_content:
            # Calcula a redução com base na quantidade de palavras-chave encontradas
            # Quanto mais palavras não relacionadas, maior a redução
            reduction_factor = min(0.7, 0.2 + (len(non_system_words) * 0.1))
            logger.info(f"Contexto contém {len(non_system_words)} palavras-chave não relacionadas ao sistema: {', '.join(non_system_words[:5])}. Reduzindo relevância.")
            best_match_score = best_match_score * reduction_factor
        
        # Verifica se o score está abaixo do threshold mínimo
        if best_match_score < self.minimum_relevance_threshold:
            logger.info(f"Score de relevância muito baixo: {best_match_score:.2f} (original: {original_score:.2f}). Considerando contexto irrelevante.")
            return {
                "is_relevant": False,
                "relevance_level": "irrelevant",
                "response_type": "irrelevant_context",
                "best_score": best_match_score,
                "original_score": original_score
            }
        
        # Avalia a relevância com base nos thresholds
        if best_match_score >= self.relevance_thresholds["high"]:
            return {
                "is_relevant": True,
                "relevance_level": "high",
                "response_type": "context_based",
                "best_score": best_match_score,
                "original_score": original_score
            }
        elif best_match_score >= self.relevance_thresholds["medium"]:
            return {
                "is_relevant": True,
                "relevance_level": "medium",
                "response_type": "context_based",
                "best_score": best_match_score,
                "original_score": original_score
            }
        elif best_match_score >= self.relevance_thresholds["low"]:
            return {
                "is_relevant": True,
                "relevance_level": "low",
                "response_type": "context_based_uncertain",
                "best_score": best_match_score,
                "original_score": original_score
            }
        elif best_match_score >= self.relevance_thresholds["very_low"]:
            return {
                "is_relevant": False,
                "relevance_level": "very_low",
                "response_type": "very_low_relevance",
                "best_score": best_match_score,
                "original_score": original_score
            }
        else:
            return {
                "is_relevant": False,
                "relevance_level": "insufficient",
                "response_type": "clarification",
                "best_score": best_match_score,
                "original_score": original_score
            }
    
    async def send_message(
        self,
        conversation_id: str,
        content: str,
        context_results: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Envia uma mensagem e obtém resposta"""
        try:
            # Recupera a conversa
            conversation = self.get_conversation(conversation_id)
            if not conversation:
                logger.error(f"Conversa não encontrada: {conversation_id}")
                raise ValueError(f"Conversa não encontrada: {conversation_id}")
            
            # Adiciona mensagem do usuário
            user_message_id = self.conversation_store.add_message_to_conversation(
                conversation_id=conversation_id,
                user_id=self.user_id,
                role="user",
                content=content
            )
            
            # 1. CLASSIFICAÇÃO - Determina o tipo da mensagem
            message_type = await self._classify_message_intent(content, conversation)
            requires_vector_search = message_type == "SISTEMA"
            
            # Recarrega a conversa com a nova mensagem do usuário
            conversation = self.get_conversation(conversation_id)
            
            # Variáveis para controle do fluxo
            context_relevance = {
                "is_relevant": False,
                "relevance_level": "none",
                "response_type": "direct",
                "best_score": 0.0
            }
            
            # 2. BUSCA VETORIAL (se necessário)
            if requires_vector_search:
                # Busca contexto se não fornecido
                if context_results is None:
                    context_results = await self.get_context(content)
                
                # 3. AVALIAÇÃO DE RELEVÂNCIA DO CONTEXTO
                context_relevance = self._evaluate_context_relevance(context_results)
                
                logger.info(
                    f"Avaliação de contexto: {context_relevance['relevance_level']} "
                    f"(score: {context_relevance['best_score']:.2f})"
                )
            
            # Prepara mensagens para o chat
            messages = self._get_conversation_messages(conversation)
            
            # 4. PREPARAÇÃO DO PROMPT BASEADO NO TIPO DE RESPOSTA
            if requires_vector_search:
                response_type = context_relevance["response_type"]
            elif message_type == "CONHECIMENTO_GERAL":
                response_type = "general_knowledge"
            else:
                response_type = "direct"
            
            if response_type == "direct":
                # Resposta direta sem contexto (saudações, agradecimentos, etc.)
                system_prompt = """Você é um assistente útil e amigável especializado no Sistema Gestor de Documentos RAG.
                Esta mensagem não requer informações específicas do sistema.
                Responda de forma natural e amigável, mantendo a continuidade da conversa.
                Lembre-se que você só pode fornecer informações sobre o Sistema Gestor de Documentos RAG e seus processos."""
                
                # Atualiza a mensagem do sistema
                for i, msg in enumerate(messages):
                    if isinstance(msg, SystemMessage):
                        messages[i] = SystemMessage(content=system_prompt)
                        break
                
                # Adiciona a mensagem do usuário
                messages.append(HumanMessage(content=content))
            
            elif response_type == "general_knowledge":
                # Resposta para perguntas de conhecimento geral
                system_prompt = """Você é um assistente útil e amigável especializado no Sistema Gestor de Documentos RAG.
                Esta mensagem é sobre conhecimento geral não relacionado ao Sistema Gestor de Documentos RAG.
                Explique educadamente que você é especializado em responder perguntas sobre o Sistema Gestor de Documentos RAG e seus processos,
                e que não possui informações específicas sobre temas gerais como esportes, entretenimento, etc.
                Ofereça ajudar com perguntas relacionadas ao Sistema Gestor de Documentos RAG, como processar documentos, listar documentos, 
                remover documentos ou buscar informações nos documentos armazenados."""
                
                # Atualiza a mensagem do sistema
                for i, msg in enumerate(messages):
                    if isinstance(msg, SystemMessage):
                        messages[i] = SystemMessage(content=system_prompt)
                        break
                
                # Adiciona a mensagem do usuário
                messages.append(HumanMessage(content=content))
            
            elif response_type == "context_based":
                # Resposta baseada em contexto relevante
                system_prompt = """Você é um assistente especializado no Sistema Gestor de Documentos RAG.
                Use APENAS as informações do contexto fornecido para responder à pergunta.
                Seja detalhado e preciso, fornecendo instruções claras quando aplicável.
                Não invente informações que não estejam no contexto fornecido."""
                
                # Atualiza a mensagem do sistema
                for i, msg in enumerate(messages):
                    if isinstance(msg, SystemMessage):
                        messages[i] = SystemMessage(content=system_prompt)
                        break
                
                # Formata o contexto
                context_text = self._format_context(context_results)
                
                # Adiciona a mensagem com contexto
                messages.append(HumanMessage(content=f"{content}\n\n{context_text}"))
            
            elif response_type == "context_based_uncertain":
                # Resposta baseada em contexto de baixa relevância
                system_prompt = """Você é um assistente especializado no Sistema Gestor de Documentos RAG.
                Encontrei algumas informações que podem estar relacionadas à pergunta, mas não tenho certeza se são exatamente o que o usuário procura.
                Forneça a melhor resposta possível com base no contexto, mas indique que o usuário pode precisar fornecer mais detalhes se a resposta não for satisfatória.
                Esclareça que você só pode responder perguntas relacionadas ao Sistema Gestor de Documentos RAG e seus processos."""
                
                # Atualiza a mensagem do sistema
                for i, msg in enumerate(messages):
                    if isinstance(msg, SystemMessage):
                        messages[i] = SystemMessage(content=system_prompt)
                        break
                
                # Formata o contexto
                context_text = self._format_context(context_results)
                
                # Adiciona a mensagem com contexto
                messages.append(HumanMessage(content=f"{content}\n\n{context_text}"))
            
            elif response_type == "very_low_relevance":
                # Resposta para contexto com relevância muito baixa
                system_prompt = """Você é um assistente especializado no Sistema Gestor de Documentos RAG.
                Encontrei algumas informações nos documentos da empresa, mas elas têm relevância muito baixa para a pergunta.
                Explique educadamente que as informações encontradas não parecem ser suficientes para responder adequadamente à pergunta.
                Peça ao usuário para fornecer mais detalhes específicos ou reformular a pergunta para focar no Sistema Gestor de Documentos RAG.
                Sugira exemplos de perguntas relacionadas ao Sistema Gestor de Documentos RAG, como processar documentos, listar documentos, 
                remover documentos ou buscar informações nos documentos armazenados."""
                
                # Atualiza a mensagem do sistema
                for i, msg in enumerate(messages):
                    if isinstance(msg, SystemMessage):
                        messages[i] = SystemMessage(content=system_prompt)
                        break
                
                # Adiciona a mensagem sem contexto
                messages.append(HumanMessage(content=content))
            
            elif response_type == "irrelevant_context":
                # Resposta para contexto completamente irrelevante
                system_prompt = """Você é um assistente especializado no Sistema Gestor de Documentos RAG.
                
                Sua pergunta parece estar relacionada a um sistema ou processo, mas não encontrei informações relevantes 
                nos documentos da empresa que possam responder adequadamente.
                
                Explique educadamente que você só pode fornecer informações sobre o Sistema Gestor de Documentos RAG 
                e seus processos relacionados, conforme documentado nos arquivos da empresa.
                
                Esclareça que não possui informações sobre outros sistemas, produtos ou serviços não relacionados.
                
                Sugira que o usuário reformule a pergunta para focar especificamente no Sistema Gestor de Documentos RAG,
                como por exemplo perguntas sobre como processar documentos, listar documentos, remover documentos ou
                buscar informações nos documentos armazenados."""
                
                # Atualiza a mensagem do sistema
                for i, msg in enumerate(messages):
                    if isinstance(msg, SystemMessage):
                        messages[i] = SystemMessage(content=system_prompt)
                        break
                
                # Adiciona a mensagem sem contexto
                messages.append(HumanMessage(content=content))
            
            elif response_type == "clarification":
                # Resposta pedindo esclarecimento
                system_prompt = """Você é um assistente especializado no Sistema Gestor de Documentos RAG.
                Não encontrei informações específicas sobre esta pergunta nos documentos da empresa.
                Peça educadamente ao usuário para fornecer mais detalhes ou reformular a pergunta, explicando que você só pode responder 
                perguntas relacionadas ao Sistema Gestor de Documentos RAG e seus processos.
                Sugira exemplos de perguntas que você pode responder, como processar documentos, listar documentos, 
                remover documentos ou buscar informações nos documentos armazenados."""
                
                # Atualiza a mensagem do sistema
                for i, msg in enumerate(messages):
                    if isinstance(msg, SystemMessage):
                        messages[i] = SystemMessage(content=system_prompt)
                        break
                
                # Adiciona a mensagem sem contexto
                messages.append(HumanMessage(content=content))
            
            # 5. GERAÇÃO DA RESPOSTA
            response = await self.chat.ainvoke(messages)
            
            # 6. PREPARAÇÃO DOS METADADOS
            metadata = {
                "response_type": response_type,
                "required_vector_search": requires_vector_search
            }
            
            if requires_vector_search and context_results and len(context_results) > 0:
                best_context = context_results[0]
                metadata.update({
                    "context_source": best_context["metadata"].get("source", ""),
                    "doc_id": best_context["metadata"].get("doc_id", ""),
                    "chunk_index": best_context["metadata"].get("chunk_index", 0),
                    "similarity_score": best_context["score"],
                    "relevance_level": context_relevance["relevance_level"]
                })
            
            # Salva resposta
            assistant_message_id = self.conversation_store.add_message_to_conversation(
                conversation_id=conversation_id,
                user_id=self.user_id,
                role="assistant",
                content=response.content,
                metadata=metadata
            )
            
            # Recarrega a conversa para obter a mensagem completa
            conversation = self.get_conversation(conversation_id)
            assistant_message = None
            for msg in conversation.messages:
                if msg["id"] == assistant_message_id:
                    assistant_message = msg
                    break
            
            return assistant_message or {"role": "assistant", "content": response.content}
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            raise 

    async def get_response(self, conversation_id: str, message: str) -> Dict[str, Any]:
        """
        Processa uma mensagem do usuário e obtém uma resposta.
        Este método é um wrapper para o método send_message.
        
        Args:
            conversation_id: ID da conversa
            message: Mensagem do usuário
            
        Returns:
            Dict com a resposta do assistente
        """
        try:
            # Obtém a resposta usando o método send_message diretamente
            # O método send_message já adiciona a mensagem do usuário à conversa
            response = await self.send_message(conversation_id, message)
            
            return response
        except Exception as e:
            logger.error(f"Erro ao obter resposta: {str(e)}")
            return {
                "role": "assistant",
                "content": f"Ocorreu um erro ao processar sua mensagem: {str(e)}",
                "sources": []
            }
    
    def add_message(self, conversation_id: str, role: str, content: str, metadata: Dict[str, Any] = None) -> str:
        """
        Adiciona uma mensagem à conversa.
        
        Args:
            conversation_id: ID da conversa
            role: Papel da mensagem (user, assistant, system)
            content: Conteúdo da mensagem
            metadata: Metadados adicionais
            
        Returns:
            ID da mensagem adicionada
        """
        return self.conversation_store.add_message_to_conversation(
            conversation_id=conversation_id,
            user_id=self.user_id,
            role=role,
            content=content,
            metadata=metadata
        ) 