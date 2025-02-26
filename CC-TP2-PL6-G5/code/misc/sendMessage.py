import socket
import struct 

def sendMessage(socket, addr, data, messageType):
        """
        Sends a UDP datagram with the provided data and message type to a specified address.

        This function constructs a UDP datagram by packing header and message data, 
        including the source port, destination port, sequence number, and message type.
        The data is split into chunks if it's too large, and each chunk is sent separately 
        as a part of the UDP datagram. The function handles the packing of the UDP header 
        and additional protocol-specific fields before sending the datagram over the network.

        Behavior:
           - Builds the UDP header and message for each chunk of data.
           - Sends each chunk to the specified destination address.
           - Handles different message types by packing different header information.
           - Chunks data if it's too large to fit into a single UDP datagram.

        Args:
           socket (socket.socket): The socket object used to send the datagram.
           addr (tuple): The destination address (IP, port) to which the datagram is sent.
           data (str): The data to be sent in the datagram, which will be encoded to bytes.
           messageType (int): An integer representing the type of message being sent.

        Example:
           >>> sendMessage(socket, ('10.0.0.2', 8080), "Hello, World!", 1)
        """

        # Build the UDP datagram with the defined structure
        source_port = socket.getsockname()[1]  # Source port (can be configurable)
        dest_port = addr[1]

        data = data.encode('utf-8')

        chunk_size = 512
        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

        sequence_number = 0
        sequence_length = len(chunks)

        for info in chunks:
      

            # UDP header fields
            length = 14 + len(info)  # UDP header (8 bytes) + data
            checksum = 0  # Simulated, checksum calculation not implemented

            if messageType == 5 and sequence_number != 0:
               udp_header = struct.pack('!HHHHH', source_port, dest_port, length, checksum, 1)
            else:
            # Pack the UDP header fields
               udp_header = struct.pack('!HHHHH', source_port, dest_port, length, checksum, messageType)

            # Pack additional protocol fields
            message = struct.pack('!HH', sequence_number, sequence_length) + info

            sequence_number += 1
        
            # Combine the UDP header with the message
            datagram = udp_header + message

            #print(f"datagram: {datagram}\n")
        
            # Send the datagram to the server
            socket.sendto(datagram, addr)
            #print(f"Datagram sent: Seq: {sequence_number}, Type: {message_type}, Data: {data.decode('utf-8')}")
