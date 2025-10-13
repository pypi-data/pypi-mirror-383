#!/usr/bin/env python3
"""
Basic Usage Example - Cost Katana Python SDK

This example shows the simplest way to use Cost Katana.
"""

import cost_katana as ck


def main():
    print("🥷 Cost Katana - Basic Usage Example")
    print("=" * 50)
    
    # Step 1: Configure (one-time setup)
    api_key = input("Enter your Cost Katana API key (or press Enter to skip): ").strip()
    
    if api_key:
        ck.configure(api_key=api_key)
        print("✅ Configured with your API key\n")
    else:
        print("⚠️  Using API key from environment (COST_KATANA_KEY)\n")
    
    # Step 2: Use the simple API
    print("📝 Example 1: Simple Question")
    print("-" * 50)
    
    response = ck.ai('gemini-2.0-flash', 'What is Python?')
    
    print(f"Response: {response.text[:200]}...")
    print(f"💰 Cost: ${response.cost:.6f}")
    print(f"🔢 Tokens: {response.tokens}")
    print(f"🤖 Model: {response.model}")
    print(f"📡 Provider: {response.provider}")
    print()
    
    # Step 3: Try different models
    print("📝 Example 2: Model Comparison")
    print("-" * 50)
    
    models = ['gpt-3.5-turbo', 'claude-3-haiku', 'gemini-flash']
    prompt = 'Explain AI in one sentence'
    
    for model in models:
        try:
            response = ck.ai(model, prompt)
            print(f"{model:20s} ${response.cost:.6f}")
        except Exception as e:
            print(f"{model:20s} Error: {str(e)[:50]}")
    
    print()
    
    # Step 4: Chat conversation
    print("📝 Example 3: Chat Session")
    print("-" * 50)
    
    chat = ck.chat('gpt-3.5-turbo')
    
    print("User: Hello!")
    response1 = chat.send('Hello!')
    print(f"AI: {response1}\n")
    
    print("User: What can you help me with?")
    response2 = chat.send('What can you help me with?')
    print(f"AI: {response2}\n")
    
    print(f"💰 Total conversation cost: ${chat.total_cost:.6f}")
    print(f"📊 Total messages: {len(chat.history)}")
    print()
    
    # Step 5: Enable optimization
    print("📝 Example 4: Cost Optimization")
    print("-" * 50)
    
    # Without optimization
    standard = ck.ai('gpt-4', 'Write a short poem about coding')
    print(f"Standard cost: ${standard.cost:.6f}")
    
    # With Cortex optimization
    optimized = ck.ai('gpt-4', 'Write a short poem about coding', cortex=True)
    print(f"Optimized cost: ${optimized.cost:.6f}")
    
    savings = standard.cost - optimized.cost
    if savings > 0:
        percent = (savings / standard.cost) * 100
        print(f"💰 Saved: ${savings:.6f} ({percent:.1f}%)")
    print()
    
    # Step 6: Smart caching
    print("📝 Example 5: Smart Caching")
    print("-" * 50)
    
    # First call - costs money
    r1 = ck.ai('gpt-3.5-turbo', 'What is 2+2?', cache=True)
    print(f"First call: ${r1.cost:.6f}, Cached: {r1.cached}")
    
    # Second call - free from cache
    r2 = ck.ai('gpt-3.5-turbo', 'What is 2+2?', cache=True)
    print(f"Second call: ${r2.cost:.6f}, Cached: {r2.cached}")
    print()
    
    print("✅ All examples completed successfully!")
    print()
    print("💡 Next steps:")
    print("  • Visit your dashboard: https://costkatana.com/dashboard")
    print("  • Check out more examples in the examples/ folder")
    print("  • Read the docs: https://docs.costkatana.com/python")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure you have:")
        print("  1. Set your API key: export COST_KATANA_KEY='dak_...'")
        print("  2. Active internet connection")
        print("  3. Valid Cost Katana account at costkatana.com")
