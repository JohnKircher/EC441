####################################################
# DVrouter.py
# Name: John Kircher, Julian Padgett
# BU ID: U61489057, U45478831
#####################################################

import sys 
from collections import defaultdict
from router import Router
from packet import Packet
from json import dumps, loads

INFINITY = 16

class DVrouter(Router):
    """Distance vector routing protocol implementation."""

    def __init__(self, addr, heartbeatTime):
        """TODO: add your own class fields and initialization code here"""
        Router.__init__(self, addr)  # initialize superclass - don't remove
        self.heartbeatTime = heartbeatTime
        self.last_time = 0
        # Hints: initialize local state
        
        self.addr = addr #ADDRESS
        self.fwd_tb2 = {}
        #Our Forwarding Table
        ####################
        self.fwd_tb = {addr: {"destination": None, "next_hop": None, "cost": 0}}
        #####################
        
       

        #self.infinity = 16
        
    def broadcast(self):
        #broadcast signal 
        # The router creates this data packet, seen on line 40
        for addr1, distance_vector1 in self.fwd_tb.iteritems():
            #json.dumps() function converts a Python object into a json string.
         #this is good for us because we want to have the forwarding table 
            #information look nice as: source, destination, cost.
 
            #However, loads is going to decode the forwarding table se we can uss iteritems on it. 
            contents = loads(dumps(self.fwd_tb)) # storing the data into contents. 
            for i, j in contents.iteritems():
                #after looping through, once we find the next host, we set the contents below. 
                if i == j["next_hop"]:
                    contents[i] = {
                        "cost": INFINITY,
                        "next_hop": None,
                        "destination": None
                    }
            #going to be sent to each destination one by one. 
            #so we are going to have multiple copies of a single data paket
            #with differetn addr's
            packet = Packet(Packet.ROUTING, self.addr, addr1, dumps(contents))
            self.send(distance_vector1["destination"], packet)


    ###IGNORE THIS, bellman_ford now done inside of handle packet
    #def bellman_ford(self, content):
        #update the node, bellman_ford for ditance vector algorithm
        #first use load to decode what dumps has done to the content. 
        #data = loads(content)
        #put each piece into source, destination and cost, this will be utilized throughout the program
        #source = data["source"]
        #destination = data["destination"]
        #cost = data["cost"]
        #now we need to create the links between the source and the destination. 
        #First check if the current node can actually reach the destination, 
        #if it can't we need to make a new conenction. 
        #if destination not in self.cost:
            #if source in self.cost:
                #the destination distance will be the source distance + that distance
                #the next_hop will be the destination will be the source
                #return
                #self.cost[destination] = self.cost[source] + cost
                #self.next_hop[destination] = self.next_hop[source]
                #return True, destination, self.cost[destination]
        
        #if it is, then we need to choose either the better distance or the new information
        #if destination in self.cost:
            #if source in self.cost:
                # A couple things are going on here. 
                #first, the distance from the source to its destination could find a better distance be reduced, 
                #so, hte current node also needs to be reduced with the new distance/cost. 
                #however, it could also be the case that the link was disconnected, and the distance 
                #needs to become self.infinity. 
                #so then the route from the current node to its destination
                #needs to be updated. 
                #if (self.cost[destination] > self.cost[source] + cost) or (self.cost[destination] < self.cost[source] + cost and self.next_hop[destination] == source and source != destination):
                    #update the node with the new distance
                    #self.cost[destination] = self.cost[source] + cost
                    #, and correct the source. 
                    #self.next_hop[destination] = self.next_hop[source]
                    #if it has been disconnected, we need to set it back to infinity. 
                    #if self.cost[destination] > INFINITY:
                    #   self.cost[destination] = INFINITY
                    #return
                    #return True, destination, self.cost[destination]

        #return None



    def handlePacket(self, port, packet):
        """TODO: process incoming packet"""
        if packet.isTraceroute(): #if packet is traceroute
            # Hints: this is a normal data packet
            # if the forwarding table contains packet.dstAddr
            #   send packet based on forwarding table, e.g., self.send(port, packet)
            if packet.dstAddr in self.fwd_tb: #if the packet is in forwarding table
                # assign the destination address from the forwarding table to what we are forwarding.
                #send function as explained above, with the port, packet. 
                self.send(self.fwd_tb[packet.dstAddr]["destination"], packet) #send port then packet from forwarding table
        
        #now if the received distance vector is different, 
        #we need to update not only the local copy, but the distance vector of the router, the 
        #forwarding table, and we also need to broadcast the distance vector to all the neighbors. 
        else:
            distance_vector_data = loads(packet.content)
            # if the received distance vector is different
            # Hints: this is a routing packet generated by your routing protocol
            #could be (if node != None) 
            for addr, distance_vector in distance_vector_data.iteritems():
                if addr != self.addr:
                    #now we need to create the links between the source and the destination. 
                    #First check if the current node can actually reach the destination, 
                    #if it can't we need to make a new conenction.
                    if addr not in self.fwd_tb:
                        if self.fwd_tb[packet.srcAddr]["destination"] is not None:
                            #   update the distance vector of this router
                            #   update the forwarding table
                            self.fwd_tb[addr] = {
                                "cost": self.fwd_tb[packet.srcAddr]["cost"] + distance_vector["cost"],
                                "next_hop": packet.srcAddr,
                                "destination": self.fwd_tb[packet.srcAddr]["destination"]
                            }
                
                    #if it is, then we need to choose either the better distance or the new information

                    else:
                        # A couple things are going on here. 
                        #first, the distance from the source to its destination could find a better distance be reduced, 
                        #so, hte current node also needs to be reduced with the new distance/cost. 
                        #however, it could also be the case that the link was disconnected, and the distance 
                        #needs to become self.infinity. 
                        #so then the route from the current node to its destination
                        #needs to be updated. 
                        if (self.fwd_tb[packet.srcAddr]["cost"] + distance_vector["cost"] < self.fwd_tb[addr]["cost"]) and self.fwd_tb[packet.srcAddr]["destination"] is not None:
                            #   update the distance vector of this router
                            #   update the forwarding table
                            self.fwd_tb[addr] = {
                                "cost": self.fwd_tb[packet.srcAddr]["cost"] + distance_vector["cost"],
                                "next_hop": packet.srcAddr,
                                "destination": self.fwd_tb[packet.srcAddr]["destination"]
                            }
                        elif self.fwd_tb[addr]["next_hop"] == packet.srcAddr:
                            #   update the distance vector of this router
                            #   update the forwarding table
                            self.fwd_tb[addr] = {
                                "cost": self.fwd_tb[packet.srcAddr]["cost"] + distance_vector["cost"],
                                "next_hop": packet.srcAddr,
                                "destination": self.fwd_tb[packet.srcAddr]["destination"]
                            }
                #json.dumps() function converts a Python object into a json string.
                #this is good for us because we want to have the forwarding table 
                #information look nice as: source, destination, cost. 
            if dumps(self.fwd_tb2) != dumps(self.fwd_tb):
                self.fwd_tb2 = self.fwd_tb
                #   broadcast the distance vector of this router to neighbors
                self.broadcast()
             
               
    def handleNewLink(self, port, endpoint, cost):
        """TODO: handle new link"""
        # update the distance vector of this router
        #make sure that the new endpoint is not in the fwd table, or that the cost of that new link is not less than the cost given
        if endpoint not in self.fwd_tb or self.fwd_tb[endpoint]["cost"] > cost:
            # update the forwarding table
            self.fwd_tb[endpoint] = {
                "cost": cost, 
                "next_hop": endpoint, 
                "destination": port}

        self.fwd_tb2 = self.fwd_tb
        # broadcast the distance vector of this router to neighbors
        self.broadcast()


    def handleRemoveLink(self, port):
        """TODO: handle removed link"""
        # update the distance vector of this router
        # update the forwarding table
        # broadcast the distance vector of this router to neighbors
        # using the port of the giving link to be removed, get the address. 

        #It is important to delete all the currect shortest paths that pass through the 
        #given link according to the given port and set it to infiinty. 
        for addr, distance_vector in self.fwd_tb.iteritems():

            #looking at all the other connections in the network
            #if the one we are looking at is what we need to remove, then we will set it's distance to infinity
            if distance_vector["destination"] == port:
                #delete the port of the given router.
                self.fwd_tb[addr] = {
                    "cost": INFINITY, 
                    "next_hop": None, 
                    "destination": None
                }
                #this is done for each connection
        self.fwd_tb2 = self.fwd_tb
        self.broadcast()

            
    def handleTime(self, timeMillisecs):
        """TODO: handle current time"""
        #goal here is to updated the routing information frequently
        #so I assume we need to just send the routing packet to neighboring nodes. 
        if timeMillisecs - self.last_time >= self.heartbeatTime:
            self.last_time = timeMillisecs
            # need to go through all the neighbors and send the distance of each node
            # that is avaiable by the current node we want to look at. 
            #Then we will do the same things as before, we just send the routing packet to the neighboring nodes. 
            self.fwd_tb2 = self.fwd_tb
            for addr, distance_vector in self.fwd_tb.iteritems():
                #broadcast the distance vector to its neighbors. 
                packet = Packet(Packet.ROUTING, self.addr, addr, dumps(self.fwd_tb))
                self.send(distance_vector["destination"], packet)
           


    def debugString(self):
        """TODO: generate a string for debugging in network visualizer"""
        #jonathan said to just print out the fwd_tbl
        debug_string = str(self.fwd_tb) + "\n\n"

        #for some reason the \n's are not working here but I finally passed all tests. 
        return debug_string
