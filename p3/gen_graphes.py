from alertes import GraphGenerator
import os
import sys
import time

def main():
    try:
        graph_generator = GraphGenerator()
        graph_generator.generate_all_graphs()

    except Exception as e:
        print(f"Erreur lors de la génération des graphiques: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())