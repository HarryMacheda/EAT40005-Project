from abstracts.AAdapter import AAdapter
import struct

START_CODE:bytes  =  b'\xFF\xFF\xFF\xFF'
END_CODE:bytes = b'\x00\x00\x00\x00'

class PointStreamAdapter(AAdapter[object, bytes]):
    @staticmethod
    def Encode(input:object) -> bytes:
        #converts an array of [x,y,z] arrays
        byte_array = bytearray()
        byte_array.extend(START_CODE)
        for point in input:
            byte_array.extend(struct.pack('f',point[0]))
            byte_array.extend(struct.pack('f',point[1]))
            byte_array.extend(struct.pack('f',point[2]))
        byte_array.extend(END_CODE)

        return byte_array

    @staticmethod
    def Decode(input:bytes) -> object:
        if not input.startswith(START_CODE) or not input.endswith(END_CODE):
            raise ValueError("Invalid start or end code")
        
        input = input[len(START_CODE):-len(END_CODE)]

        result = []
        for i in range(0, len(input), 12):
            x = struct.unpack('f', input[i:i+4])[0]  
            y = struct.unpack('f', input[i+4:i+8])[0]
            z = struct.unpack('f', input[i+8:i+12])[0]
            result.append([x, y, z])

        return result
