"""
UMass ECE 241 - Advanced Programming
Project 2 - Fall 2023
"""
import sys
from graph import Graph, Vertex
from priority_queue import PriorityQueue, Queue


class DeliveryService:
    def __init__(self) -> None:
        """
        Constructor of the Delivery Service class
        """
        self.city_map = None
        self.MST = None

    def buildMap(self, filename: str) -> None:
        self.city_map = Graph()
        with open(filename, 'r') as file:
            for line in file:
                data = line.strip().split('|')
                node1, node2, cost = int(data[0]), int(data[1]), int(data[2])
                # Add edges with weights to the city map
                self.city_map.addEdge(node1, node2, cost)
                # Assuming the links are bi-directional, add the reverse edges as well
                self.city_map.addEdge(node2, node1, cost)

    def isWithinServiceRange(self, restaurant: int, user: int, threshold: int) -> bool:
        if self.city_map.getVertex(user) is None:
            return False  # User does not exist

        distances = {v.getId(): float('inf') for v in self.city_map}

        distances[restaurant] = 0  # Initialize the restaurant distance as 0

        queue = [restaurant]  # Initialize the queue for BFS traversal
        while queue:
            current_vertex = queue.pop(0)

            for neighbor in self.city_map.getVertex(current_vertex).getConnections():
                weight = self.city_map.getVertex(current_vertex).getWeight(neighbor)
                # Update distance if it's shorter and within the threshold, and add the neighbor to the queue
                if distances[neighbor.getId()] == float('inf') or distances[neighbor.getId()] > distances[
                    current_vertex] + weight:
                    distances[neighbor.getId()] = distances[current_vertex] + weight
                    if distances[neighbor.getId()] <= threshold:
                        queue.append(neighbor.getId())

        # Return True if the user distance is within the threshold, False otherwise
        return distances[user] <= threshold

    #

    def buildMST(self, restaurant):
        self.MST = Graph()  # Initialize a new graph for the MST
        pq = PriorityQueue()  # Priority queue to keep track of edge costs

        # Initialize distances and predecessors for all vertices
        for v in self.city_map:
            v.setDistance(sys.maxsize)
            v.setPred(None)

        rest_vertex = self.city_map.getVertex(restaurant)
        rest_vertex.setDistance(0)  # Initialize the restaurant's distance as 0
        pq.buildHeap([(v.getDistance(), v) for v in self.city_map])  # Initialize the priority queue

        while not pq.isEmpty():
            currentVert = pq.delMin()  # Get the vertex with the minimum distance

            for nextVert in currentVert.getConnections():
                newCost = currentVert.getWeight(nextVert)
                if nextVert in pq and newCost < nextVert.getDistance():
                    nextVert.setPred(currentVert)  # Update predecessor
                    nextVert.setDistance(newCost)  # Update distance
                    pq.decreaseKey(nextVert, newCost)  # Update priority queue

        # Construct the MST using the predecessors
        for v in self.city_map:
            if v.getPred() is not None:
                self.MST.addEdge(v.getPred().getId(), v.getId(), v.getDistance())

    def minimalDeliveryTime(self, restaurant, user):
        if restaurant not in self.MST or user not in self.MST:
            return -1  # Return -1 if either node does not exist in the MST

        start_vertex = self.MST.getVertex(restaurant)


        distances = {v.getId(): float('inf') for v in self.MST}  # Use vertex IDs for initialization
        distances[start_vertex.getId()] = 0  # Initialize the distance of the start vertex as 0

        queue = PriorityQueue()
        queue.buildHeap([(0, start_vertex)])  # Initialize the queue with the start vertex

        while not queue.isEmpty():
            current_vertex = queue.delMin()

            for neighbor in self.MST.getVertex(current_vertex.getId()).getConnections():
                weight = self.MST.getVertex(current_vertex.getId()).getWeight(neighbor)
                if distances[current_vertex.getId()] + weight < distances[neighbor.getId()]:
                    distances[neighbor.getId()] = distances[current_vertex.getId()] + weight
                    queue.add((distances[neighbor.getId()], neighbor))  # Add neighbor Vertex object to the queue

        minimal_time = distances[user]
        if minimal_time == float('inf'):
            return -1  # If the user is not reachable from the restaurant, return -1
        return minimal_time

    def findDeliveryPath(self, restaurant, user):
        restaurant = self.city_map.getVertex(restaurant)
        user = self.city_map.getVertex(user)

        if user is None or restaurant is None: # Checks if either the user or restaurant is not in the city map
            return "INVALID"

        for v in self.city_map:
            v.setDistance(float('inf')) #initializes distances of all nodes by setting to inifinity
            v.setPred(None) #initializes predecessor of all nodes

        restaurant.setDistance(0) #setting restaurant as starting point
        vertQueue = Queue() # queue for BFS
        vertQueue.enqueue(restaurant)

        while vertQueue.size() > 0:
            currentVert = vertQueue.dequeue()

            for nextVert in currentVert.getConnections(): #explored neighbours
                edge_weight = currentVert.getWeight(nextVert)

                if nextVert.getDistance() > edge_weight + currentVert.getDistance() :
                    nextVert.setDistance(edge_weight + currentVert.getDistance()) #updates distance and predecessor
                    nextVert.setPred(currentVert)
                    vertQueue.enqueue(nextVert) #enqueue to continue traversal


        path = [] # Reconstructing the path based on calculated distances
        current_node = user

        while current_node is not None:
            path.insert(0, current_node)
            current_node = current_node.getPred()

        if path[0].getId() != restaurant.getId():
            return "INVALID"

        delivery_time = user.getDistance()
        path_id = [str(v.getId()) for v in path]
        path_diagram = "->".join(path_id) + f" ({delivery_time})"

        return path_diagram

    def findDeliveryPathWithDelay(self, restaurant, user, delay_info):
        restaurant = self.city_map.getVertex(restaurant)
        user = self.city_map.getVertex(user)

        if user is None or restaurant is None:
            return "INVALID"

        for v in self.city_map:
            v.setDistance(float('inf'))
            v.setPred(None)

        restaurant.setDistance(0)
        vertQueue = Queue()
        vertQueue.enqueue(restaurant)

        while vertQueue.size() > 0:
            currentVert = vertQueue.dequeue()

            for nextVert in currentVert.getConnections():
                edge_weight = currentVert.getWeight(nextVert)
                delay = delay_info.get(nextVert.getId(), 0)


                if edge_weight + delay + currentVert.getDistance() < nextVert.getDistance():
                    nextVert.setDistance(edge_weight + delay + currentVert.getDistance())
                    nextVert.setPred(currentVert)
                    vertQueue.enqueue(nextVert)


        path = []
        current_node = user
        while current_node is not None:
            path.append(str(current_node.getId()))
            current_node = current_node.getPred()

        path = path[::-1]  # Reverses the path to get the correct order
        delivery_time = user.getDistance()

        if delivery_time == float('inf'):
            return "INVALID"  # return INVALID If the user is not reachable from the restaurant

        return '->'.join(path) + f" ({delivery_time})"

    ## DO NOT MODIFY CODE BELOW!
    @staticmethod
    def nodeEdgeWeight(v):
        return sum([w for w in v.connectedTo.values()])

    @staticmethod
    def totalEdgeWeight(g):
        return sum([DeliveryService.nodeEdgeWeight(v) for v in g]) // 2

    @staticmethod
    def checkMST(g):
        for v in g:
            v.color = 'white'

        for v in g:
            if v.color == 'white' and not DeliveryService.DFS(g, v):
                return 'Your MST contains circles'
        return 'MST'

    @staticmethod
    def DFS(g, v):
        v.color = 'gray'
        for nextVertex in v.getConnections():
            if nextVertex.color == 'white':
                if not DeliveryService.DFS(g, nextVertex):
                    return False
            elif nextVertex.color == 'black':
                return False
        v.color = 'black'

        return True

# NO MORE TESTING CODE BELOW!
# TO TEST YOUR CODE, MODIFY test_delivery_service.py
