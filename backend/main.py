from agents.superior_agent import SuperiorAgent
from config.config import Config
from utils.common_utils import *
from utils.imports import *

def main():
    config = Config()
    superior_agent = SuperiorAgent(config)
    conversation_history = []
    user_id = "12345"

    # Initialize conversation tracking
    init_conversation_tracking(config)
    
    # Set up signal handler for graceful exit
    setup_signal_handler(conversation_history, config)
    
    # Counter for periodic saves
    message_count = 0

    print("Welcome to the MedAI Assistant! Type your symptoms or 'q' to quit.\n")
    while True:
        query = input("User: ")
        if query.lower() == 'q':
            # Save conversation history to a file before exiting
            save_conversation(conversation_history, config, is_final=True)
            print("___________________")
            print(conversation_history)
            break
        
        # keep track of session and user conversation
        conversation_history.append({"role": "user", "text": query})
        message_count += 1

        # find specialist
        specialty = superior_agent.determine_specialty(query)
        if specialty:
            # route to specialized agent
            agent = superior_agent.specialist_agents.get(specialty)
            if agent:
                # generate response with conversation history into account
                response = agent.handle_query(conversation_history)
                conversation_history.append({"role": "model", "agent": specialty, "text": response})
                print(f"\nModel: {response}")
                message_count += 1
                
                # Save periodically (every 3 messages)
                if message_count % 3 == 0:
                    save_conversation(conversation_history, config)
            else:
                config.logger.warning(f"@main.py No specialist agent found, {specialty}")
                conversation_history.append({"role": "model", "agent": None, "text": specialty})
        else:
            config.logger.warning("@main.py Could not determine specialty.")
            conversation_history.append({"role": "model", "agent": None, "text": "Could not determine specialty."})

if __name__ == "__main__":
    main()