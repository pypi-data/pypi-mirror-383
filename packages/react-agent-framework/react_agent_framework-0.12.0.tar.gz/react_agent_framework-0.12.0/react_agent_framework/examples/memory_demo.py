"""
Memory system demonstration - v0.10.0

Shows the NEW memory architecture with separation between:
- Chat Memory: Conversation history (sequential storage)
- Knowledge Memory: RAG/Semantic search (vector-based)
"""

from react_agent_framework import ReactAgent

# Chat Memory imports
from react_agent_framework.core.memory.chat import SimpleChatMemory, SQLiteChatMemory

# Knowledge Memory imports (optional)
try:
    from react_agent_framework.core.memory.knowledge import ChromaKnowledgeMemory

    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    from react_agent_framework.core.memory.knowledge import FAISSKnowledgeMemory

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


def demo_simple_chat_memory():
    """Demo 1: Simple Chat Memory (in-memory conversation history)"""
    print("=" * 80)
    print("DEMO 1: SIMPLE CHAT MEMORY (Conversation History)")
    print("=" * 80)

    agent = ReactAgent(
        name="Chat Assistant",
        provider="gpt-4o-mini",
        chat_memory=SimpleChatMemory(max_messages=50),
    )

    @agent.tool()
    def calculate(expression: str) -> str:
        """Calculate mathematical expressions"""
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"

    print("\n📝 Purpose: Store conversation history sequentially")
    print("📝 Use case: Maintain context in chat conversations\n")

    print("Conversation 1:")
    answer1 = agent.run("My name is Marcos", verbose=False)
    print(f"Q: My name is Marcos")
    print(f"A: {answer1}\n")

    print("Conversation 2 (remembers from chat history):")
    answer2 = agent.run("What is my name?", verbose=False)
    print(f"Q: What is my name?")
    print(f"A: {answer2}\n")

    print("Conversation 3:")
    answer3 = agent.run("Calculate 15 * 8", verbose=False)
    print(f"Q: Calculate 15 * 8")
    print(f"A: {answer3}\n")

    print("Conversation 4 (remembers previous conversation):")
    answer4 = agent.run("What was my previous calculation?", verbose=False)
    print(f"Q: What was my previous calculation?")
    print(f"A: {answer4}\n")

    # Memory stats
    print("💾 Memory Stats:")
    stats = agent.chat_memory.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


def demo_sqlite_chat_memory():
    """Demo 2: SQLite Chat Memory (persistent conversation history)"""
    print("\n" + "=" * 80)
    print("DEMO 2: SQLite CHAT MEMORY (Persistent Conversation) - NEW!")
    print("=" * 80)

    agent = ReactAgent(
        name="Persistent Chat Assistant",
        provider="gpt-4o-mini",
        chat_memory=SQLiteChatMemory(
            db_path="./chat_demo.db",
            session_id="user_marcos",
            max_messages=100,
        ),
    )

    @agent.tool()
    def get_time() -> str:
        """Get current time"""
        from datetime import datetime

        return datetime.now().strftime("%H:%M:%S")

    print("\n📝 Purpose: Persistent conversation history in SQLite")
    print("📝 Use case: Multi-session chatbots, customer support")
    print("📝 Features: No external dependencies, SQL queries, multi-session\n")

    print("Conversation 1:")
    answer1 = agent.run("Remember that I prefer Python over JavaScript", verbose=False)
    print(f"Q: Remember that I prefer Python over JavaScript")
    print(f"A: {answer1}\n")

    print("Conversation 2:")
    answer2 = agent.run("What programming language do I prefer?", verbose=False)
    print(f"Q: What programming language do I prefer?")
    print(f"A: {answer2}\n")

    # Memory stats
    print("💾 Memory Stats:")
    stats = agent.chat_memory.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n✨ Note: Conversation persists across restarts!")
    print(f"✨ Database: {agent.chat_memory.db_path}")


def demo_chroma_knowledge_memory():
    """Demo 3: ChromaDB Knowledge Memory (RAG/Semantic search)"""
    if not CHROMA_AVAILABLE:
        print("\n⚠️  ChromaDB not available. Install with: pip install react-agent-framework[knowledge-chroma]")
        return

    print("\n" + "=" * 80)
    print("DEMO 3: CHROMA KNOWLEDGE MEMORY (RAG / Semantic Search)")
    print("=" * 80)

    knowledge = ChromaKnowledgeMemory(
        collection_name="tech_docs",
        persist_directory="./chroma_knowledge_demo",
        embedding_function="default",
    )

    print("\n📚 Purpose: Store documents for semantic search (RAG)")
    print("📚 Use case: Document retrieval, knowledge bases, Q&A systems\n")

    # Add documents to knowledge base
    print("Adding technical documentation...")
    docs = [
        "Python was created by Guido van Rossum and first released in 1991",
        "Python emphasizes code readability with significant whitespace",
        "React is a JavaScript library for building user interfaces",
        "FastAPI is a modern, fast web framework for building APIs with Python",
        "Docker is a platform for developing, shipping, and running applications in containers",
    ]

    for doc in docs:
        knowledge.add_document(doc, metadata={"type": "technical"})

    print(f"✓ Added {len(docs)} documents to knowledge base\n")

    # Semantic search
    print("🔍 Semantic Search 1: 'Python programming language'")
    results = knowledge.search("Python programming language", top_k=2)
    for i, doc in enumerate(results, 1):
        print(f"  {i}. {doc.content}")

    print("\n🔍 Semantic Search 2: 'containerization technology'")
    results = knowledge.search("containerization technology", top_k=2)
    for i, doc in enumerate(results, 1):
        print(f"  {i}. {doc.content}")

    print("\n🔍 Semantic Search 3: 'web frameworks'")
    results = knowledge.search("web frameworks", top_k=2)
    for i, doc in enumerate(results, 1):
        print(f"  {i}. {doc.content}")

    # Stats
    print("\n💾 Knowledge Base Stats:")
    stats = knowledge.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


def demo_faiss_knowledge_memory():
    """Demo 4: FAISS Knowledge Memory (high-performance RAG)"""
    if not FAISS_AVAILABLE:
        print("\n⚠️  FAISS not available. Install with: pip install react-agent-framework[knowledge-faiss]")
        return

    print("\n" + "=" * 80)
    print("DEMO 4: FAISS KNOWLEDGE MEMORY (High-Performance RAG)")
    print("=" * 80)

    knowledge = FAISSKnowledgeMemory(
        index_path="./faiss_knowledge_demo",
        dimension=1536,  # OpenAI embedding dimension
        index_type="Flat",
        collection_name="tech_kb",
    )

    print("\n📚 Purpose: High-performance semantic search for large datasets")
    print("📚 Use case: Large-scale RAG, research, document retrieval\n")

    # Add technical documentation
    print("Adding technical documentation...")
    docs = [
        "Kubernetes is an open-source container orchestration platform",
        "Kubernetes automates deployment, scaling, and management of containerized applications",
        "Git is a distributed version control system for tracking changes in source code",
        "CI/CD stands for Continuous Integration and Continuous Deployment",
        "Microservices architecture structures an application as a collection of services",
    ]

    for doc in docs:
        knowledge.add_document(doc, metadata={"category": "devops"})

    print(f"✓ Added {len(docs)} documents to FAISS index\n")

    # Fast semantic search
    print("⚡ Fast Semantic Search 1: 'container orchestration'")
    results = knowledge.search("container orchestration", top_k=2)
    for i, doc in enumerate(results, 1):
        print(f"  {i}. {doc.content}")

    print("\n⚡ Fast Semantic Search 2: 'version control'")
    results = knowledge.search("version control", top_k=2)
    for i, doc in enumerate(results, 1):
        print(f"  {i}. {doc.content}")

    # Search with scores
    print("\n⚡ Search with similarity scores:")
    results_with_scores = knowledge.search_with_scores("deployment automation", top_k=3)
    for i, (doc, score) in enumerate(results_with_scores, 1):
        print(f"  {i}. [Score: {score:.4f}] {doc.content}")

    # Stats
    print("\n💾 Knowledge Base Stats:")
    stats = knowledge.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


def demo_combined_memory():
    """Demo 5: Combined Chat + Knowledge Memory (NEW!)"""
    if not CHROMA_AVAILABLE:
        print("\n⚠️  ChromaDB not available for combined demo")
        return

    print("\n" + "=" * 80)
    print("DEMO 5: COMBINED MEMORY (Chat + Knowledge) - NEW!")
    print("=" * 80)

    # Create knowledge base
    knowledge = ChromaKnowledgeMemory(
        collection_name="python_docs",
        persist_directory="./combined_demo_kb",
    )

    # Add Python documentation
    knowledge.add_document(
        "List comprehensions provide a concise way to create lists in Python",
        metadata={"topic": "lists"},
    )
    knowledge.add_document(
        "Decorators are a way to modify or enhance functions in Python",
        metadata={"topic": "functions"},
    )
    knowledge.add_document(
        "Context managers use 'with' statement to manage resources properly",
        metadata={"topic": "best_practices"},
    )

    # Create agent with both types of memory
    agent = ReactAgent(
        name="Python Expert",
        provider="gpt-4o-mini",
        chat_memory=SQLiteChatMemory("./combined_demo_chat.db", session_id="user_001"),
        # Note: knowledge_memory integration coming soon in ReactAgent
    )

    @agent.tool()
    def search_docs(query: str) -> str:
        """Search Python documentation"""
        results = knowledge.search(query, top_k=2)
        if not results:
            return "No documentation found"

        formatted = []
        for i, doc in enumerate(results, 1):
            formatted.append(f"{i}. {doc.content}")
        return "\n".join(formatted)

    print("\n🎯 Purpose: Combine chat history with knowledge retrieval")
    print("🎯 Chat Memory: Conversation context")
    print("🎯 Knowledge Memory: RAG for documentation\n")

    print("Conversation 1 (uses RAG):")
    answer1 = agent.run("What are list comprehensions in Python?", verbose=False)
    print(f"Q: What are list comprehensions in Python?")
    print(f"A: {answer1}\n")

    print("Conversation 2 (uses chat history + RAG):")
    answer2 = agent.run("Can you explain more about what you just mentioned?", verbose=False)
    print(f"Q: Can you explain more about what you just mentioned?")
    print(f"A: {answer2}\n")

    print("📊 Memory Usage:")
    print(f"  Chat messages: {agent.chat_memory.get_stats()['session_messages']}")
    print(f"  Knowledge documents: {knowledge.get_stats()['total_documents']}")


def demo_comparison():
    """Demo 6: Chat vs Knowledge Memory Comparison"""
    print("\n" + "=" * 80)
    print("DEMO 6: CHAT vs KNOWLEDGE MEMORY COMPARISON")
    print("=" * 80)

    print("\n📊 CHAT MEMORY (Conversation History)")
    print("-" * 80)
    print("✓ Purpose: Store sequential conversation history")
    print("✓ Storage: SQLite, in-memory")
    print("✓ Retrieval: Chronological order, keyword search")
    print("✓ Use cases:")
    print("  • Chatbots maintaining context")
    print("  • Customer support conversations")
    print("  • Multi-turn dialogues")
    print("\nImplementations:")
    print("  • SimpleChatMemory: In-memory buffer")
    print("  • SQLiteChatMemory: Persistent SQL database")

    print("\n📊 KNOWLEDGE MEMORY (RAG / Semantic Search)")
    print("-" * 80)
    print("✓ Purpose: Store documents for semantic retrieval")
    print("✓ Storage: Vector databases (ChromaDB, FAISS)")
    print("✓ Retrieval: Semantic similarity search with embeddings")
    print("✓ Use cases:")
    print("  • Retrieval Augmented Generation (RAG)")
    print("  • Document search engines")
    print("  • Q&A systems over knowledge bases")
    print("\nImplementations:")
    print("  • ChromaKnowledgeMemory: ChromaDB vector database")
    print("  • FAISSKnowledgeMemory: High-performance FAISS")

    print("\n🔑 KEY DIFFERENCES")
    print("-" * 80)
    print("| Feature          | Chat Memory        | Knowledge Memory  |")
    print("|------------------|-------------------|-------------------|")
    print("| Purpose          | Conversation      | Document search   |")
    print("| Order            | Sequential        | Similarity-based  |")
    print("| Search           | Keyword/Recent    | Semantic/Vector   |")
    print("| Persistence      | SQL/Memory        | Vector DB         |")
    print("| Best for         | Chat history      | RAG/Knowledge     |")

    print("\n💡 WHEN TO USE EACH")
    print("-" * 80)
    print("Use Chat Memory when:")
    print("  → You need to maintain conversation context")
    print("  → Order of messages matters")
    print("  → Simple keyword search is enough")

    print("\nUse Knowledge Memory when:")
    print("  → You need semantic document retrieval")
    print("  → Building RAG applications")
    print("  → Searching large knowledge bases")

    print("\nUse BOTH when:")
    print("  → Building advanced AI assistants")
    print("  → Chat needs access to knowledge base")
    print("  → Combining conversation context with RAG")


def main():
    """Run all memory demos"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "MEMORY SYSTEM DEMONSTRATION - v0.10.0" + " " * 24 + "║")
    print("║" + " " * 20 + "Chat Memory + Knowledge Memory" + " " * 27 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Demo 1: Simple Chat Memory
    demo_simple_chat_memory()

    # Demo 2: SQLite Chat Memory (NEW!)
    demo_sqlite_chat_memory()

    # Demo 3: ChromaDB Knowledge Memory
    demo_chroma_knowledge_memory()

    # Demo 4: FAISS Knowledge Memory
    demo_faiss_knowledge_memory()

    # Demo 5: Combined Memory (NEW!)
    demo_combined_memory()

    # Demo 6: Comparison
    demo_comparison()

    print("\n" + "=" * 80)
    print("✅ All demos completed!")
    print("=" * 80)
    print("\n📚 Learn more:")
    print("  • Migration Guide: MIGRATION_GUIDE.md")
    print("  • Documentation: https://marcosf63.github.io/react-agent-framework/")
    print()


if __name__ == "__main__":
    main()
