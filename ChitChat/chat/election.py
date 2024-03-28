from models import LeaderElection
from django.db import connections

def is_database_available():
    db_down = False
    
    try:
        connection = connections['default']
        cursor = connection.cursor()
    except Exception:
        db_down = True
        
    if db_down:
        elect_leader()
    
def elect_leader():
    
    # Get all nodes
    nodes = LeaderElection.objects.all()

    # Find the highest ID among nodes
    highest_id_node = max(nodes, key=lambda x: x.node_id)

    # Set the highest ID node as the leader
    for node in nodes:
        node.is_leader = (node == highest_id_node)
        node.save()