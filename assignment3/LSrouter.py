#####################################################
# LSrouter.py
# Name: John Kircher, Julian Padgett
# BU ID: U61489057, U45478831
#####################################################

import sys
from collections import defaultdict
from router import Router
from packet import Packet
from json import dumps, loads
import networkx as netx


class LSrouter(Router):
    """Link state routing protocol implementation."""

    def __init__(self, addr, heartbeatTime):
        """TODO: add your own class fields and initialization code here"""
        Router.__init__(self, addr)  # initialize superclass - don't remove
        self.heartbeatTime = heartbeatTime
        self.last_time = 0
        # Hints: initialize local state
        self.fwd_tb = dict()  #forwarding table as a dictionary
        self.port = dict()  #another dictionary that will store the ports.
        #counter
        self.count = 0
        ## LINK STATES 
        #Defaultdict is a container like dictionaries present in the module collections. 
        #Defaultdict is a sub-class of the dict class that returns a dictionary-like object. 
        #The functionality of both dictionaries and defualtdict are almost same except for the fact that defualtdict never raises a KeyError. 
        # It provides a default value for the key that does not exists.
        self.ls = defaultdict(list)
        ##
        #sequence numbers
        self.sequence_numbers = defaultdict(lambda: 0) # the key value pair here will have key, 0
        

    def Dijkstra_Update(self):
        # Here we will be using network x's graph interface to 
        #make the link states

        ### By definition, a Graph is a collection of nodes (vertices)
        ### along with identified pairs of nodes (called edges, links, etc). 
        ### In NetworkX, nodes can be any hashable object e.g., a text string, 
        ### an image, an XML object, another Graph, a customized node object, etc.

        #create graph
        graph = netx.Graph()
        #loop through the link state values
        for links in self.ls.values():
            graph.add_weighted_edges_from(links) #use  netx's function to add weighted edges for the links in link states

        # Now we can use dijkstra's to find the shortest
        #path and update the forwarding table.
        # 
        # loop through all the nodes in the current graph and look at each address. 
        #  Each node then independently calculates the next best logical 
        #  path from it to every possible destination in the network. 
        for addr in graph.nodes():
            if addr != self.addr:
                #if there is no link we want to link the next router with the shortest path
                #from dijkstra's shorttest path algorithm. Otherwise, we
                #can call the NetworkXNoPath to show that no such path exists. 
                try:
                    #this is the calculation for the shortest path using the dijksta_path algorithm. 
                    shortest_path = netx.dijkstra_path(graph, source=self.addr, target=addr)
                    #link the next router on the path to the destination address. 
                    next_address = shortest_path[1]

                    #Now check to see if the link states address is actually there
                    #for example the one we ned to get it. 
                    if next_address not in self.port:
                        continue
                    self.fwd_tb[addr] = self.port[next_address]
                #Exception for algorithms that should return a path when 
                # running on graphs where such a path does not exist.
                except netx.NetworkXNoPath:
                    pass

    def broadcast(self):
        #extremely similar to the broadcast function in DVrouter.py
        #we want to get the links and the message we want to send, and
        #simply broadcast it to the ports for the entire graph. 

        #get the links from the link state dictionary list
        links = self.ls[self.addr]
        #set the message to the current count which acts as the sequence number, and the links that we just stored. 
        payload = (self.count, links)
        #Same as DV router, don't forget to call dumps to make the data a readble string. 
        packet = Packet(Packet.ROUTING, self.addr, None, content=dumps(payload))
        #loop through the ports and send the updated information
        for port in self.port.values():
            self.send(port, packet) #send

        # update the sequence number
        self.count += 1

    def handlePacket(self, port, packet):
        """TODO: process incoming packet"""
        if packet.isTraceroute():
            # Hints: this is a normal data packet
            # if the forwarding table contains packet.dstAddr
            #   send packet based on forwarding table, e.g., self.send(port, packet)
            
            if packet.dstAddr in self.fwd_tb: #if the packet is in forwarding table
                #get the next router we want to send to and send it
                next_hop = self.fwd_tb[packet.dstAddr]
                self.send(next_hop, packet) #send
        else:
            # Hints: this is a routing packet generated by your routing protocol
            #decode the information from string form. 
            sequence_num, links = loads(packet.content)
            addr = packet.srcAddr
            prev_sequence_num = self.sequence_numbers[addr]
            #assert links
            #assert addr == links[0][0]
            #assert addr != self.addr
        
            # check the sequence number
            # if the sequence number is higher and the received link state is different
            if sequence_num >= prev_sequence_num and links != self.ls[addr]:
                # update the local copy of the link state
                self.ls[addr] = links
                # update the forwarding table with dijkstra's Update defined above
                self.Dijkstra_Update()
                # broadcast the packet to other neighbors
                for neighbor, neighbor_port in self.port.items():
                    
                    #Need to make sure that we are not broadcasting the packet to the 
                    #source here. 
                    #So check that the current neighbor and its port are not the same. 
                    #If so, then we can send. 
                    #Otherwise this was causing problems before we met with the TA. thank you. 
                    if neighbor != addr and neighbor_port != port:
                        self.send(neighbor_port, packet)

                #Finally update the latest sequence number here. 
                self.sequence_numbers[addr] = sequence_num

    def handleNewLink(self, port, endpoint, cost):
        """TODO: handle new link"""
        # update the forwarding table
        #self.Dijkstra_Update()
        # broadcast the new link state of this router to all neighbors
        #self.broadcast()
        #Before we update the forwarding table here
        #We actually have to handle the new link that is coming in with 
        #the appropraite distance. 
        #again, get the current links with the link state list
        links = self.ls[self.addr]
        #append the given endpoint, and cost to this list. 
        links.append([self.addr, endpoint, cost])
        #sort each in link in order. 
        links.sort()
        #get the new endpoint in the port dictionary. 
        self.port[endpoint] = port
        # update the forwarding table
        self.Dijkstra_Update()
        # broadcast the new link state of this router to all neighbors
        self.broadcast()

    def handleRemoveLink(self, port):
        """TODO: handle removed link"""
        # update the forwarding table
        #self.Dijkstra_Update()
        # broadcast the new link state of this router to all neighbors
        #self.broadcast()

        #First find the address that we want to remove. 
        #he zip() function returns a zip object, which is an iterator of 
        # tuples where the first item in each passed iterator is paired together, 
        #and then the second item in each passed iterator are paired together etc.
        #If the passed iterators have different lengths, the iterator with the 
        # least items decides the length of the new iterator.

        numbers, values = zip(*self.port.items())
        #this will be the address we want to remove based on
        #the given port from the function
        addr = numbers[values.index(port)]
        #remove the link!
        self.port.pop(addr)

        #Now we have to reconstruct or else the graph will be broken. 
        #reconstruct. 
        
        final = []
         #go through link states and update it with the correct amount of links.
        for i in self.ls[self.addr]:
             if i[1] != addr:
                final.append(i)

        self.ls[self.addr] = final

        #needed to add this to check self.ls[addr] as well because it 
        #was still leaving some incorrect routes. Now it works though. 
        final = []
        for i in self.ls[addr]:
            if i[1] != self.addr:
                final.append(i)

        self.ls[addr] = final

        # update the forwarding table
        self.Dijkstra_Update()
        # broadcast the new link state of this router to all neighbors
        self.broadcast()

    def handleTime(self, timeMillisecs):
        """TODO: handle current time"""
        if timeMillisecs - self.last_time >= self.heartbeatTime:
            self.last_time = timeMillisecs
            # Hints:
            # broadcast the link state of this router to all neighbors
            self.broadcast()

    def debugString(self):
        """TODO: generate a string for debugging in network visualizer"""
        #jonathan said to just print out the fwd_tbl
        debug_string = str(self.fwd_tb) + "\n\n"

        #for some reason the \n's are not working here but I finally passed all tests. 
        return debug_string