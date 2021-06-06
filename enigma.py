class PlugLead:
    """PlugLead simulation each lead connects two plugs."""    

    def __init__(self, mapping):
        self.mapping = tuple(mapping)
        if self.plugA() == self.plugB():
            raise ValueError("Unable to connect plug to itself.")

    def encode(self, character):
        """ Encode a character so that a letter will be swapped
        this replicates the lead.
        """
        if self.plugA() == character:
            return self.plugB()
        elif self.plugB() == character:
            return self.plugA()
        else:
            return character

    def plugA(self):
        return self.mapping[0]

    def plugB(self):
        return self.mapping[1]

    def __str__(self):
        return "{0}{1}".format(self.mapping[0],self.mapping[1])

class Plugboard:
    """Class that the plugboard could connect different letters, swapping their values from the keyboard.
        """
    def __init__(self):
        """ Ensure a plug only connects once"""
        self.leads = dict() 

    def add(self, lead):
        """Create a new connection"""

        if lead.plugA() not in self.leads and lead.plugB() not in self.leads:
            self.leads[lead.plugA()] = lead
            self.leads[lead.plugB()] = lead
        else:
            raise ValueError("Plug {0}-{1} is already in use".format(lead.plugA(), lead.plugB()))
            
    def encode(self, character):
        """ If the plug is conneced retrun the encoded charachter otherwise the original charachter.
        """
        if character in self.leads:
            return self.leads[character].encode(character)
        else:
            return character

    def __str__(self):
        return str(set("{0}".format(" ".join(str(self.leads[i]) for i in self.leads)).split()))


# You will need to write more classes, which can be done here or in separate files, you choose.


class Rotor:
    Multiple_Rotors = {
        'Alpha': "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        'Beta': "LEYJVCNIXWPBQMDRTAKZGFUHOS",
        'Gamma': "FSOKANUERHMBTIYCWLQPZXVGJD",
        'I': "EKMFLGDQVZNTOWYHXUSPAIBRCJQ",
        'II': "AJDKSIRUXBLHWTMCQGZNPYFVOEE",
        'III': "BDFHJLCPRTXVZNYEIWGAKMUSQOV",
        'IV': "ESOVPZJAYQUIRHXLNFTGKDCMWBJ",
        'V': "VZBRGITYUPSDNHLXAWMJQOFECKZ",
        'A': "EJMZALYXVBWFCRQUONTSPIKHGD",
        'B': "YRUHQSLDPXNGOKMIEBFZCWVJAT",
        'C': "FVPJIAOYEDRZXWGCTKUQSBNMHL",
    }

    def __init__(self, Label, left_Rotor=None, right_Rotor=None, pos=0, ring=0):
        """Inititaliase the Enigma rotor and reflector
        :param label:   A supported Rotor
        :param left_Rotor:  Left hand side rotor
        :param right_Rotor: Right hand side rotor
        :param pos:     Initial rotor position
        :param ring:    Ring setting
        """
        if Label in Rotor.Multiple_Rotors:
            self.position = pos - ring
            self.ring_setting = ring
            self.Label = Label
            self.left_rotor = left_Rotor
            self.right_rotor = right_Rotor
            self.right_pins = Rotor.Multiple_Rotors['Alpha']
            self.left_pins = Rotor.Multiple_Rotors[Label][:26]
            if len(Rotor.Multiple_Rotors[Label]) > 26:
                self.notch = Rotor.Multiple_Rotors[Label][26]
                if self.ring_setting > 0:
                    idx = self.right_pins.index(self.notch) - ring
                    self.notch = self.right_pins[idx]
            else:
                self.notch = None
        else:
            raise ValueError("Rotor {} unsupported".format(Label))
            
    def encode_left_to_right(self, character):
        """Charachter to go through right of the rotor
        :param character:   Input character to be encoded.
        :return:            Encoded character
        """
        offset = self.position
        if self.left_rotor is not None:
            offset -= self.left_rotor.get_position()
        input_pin = (self.right_pins.index(character) + offset) % 26
        pin_index = self.left_pins.index(self.right_pins[input_pin])
        return self.right_pins[pin_index]

    def encode_right_to_left(self, character):
        """Charachter to go through right of the rotor
        :param character:   Input character to be encoded.
        :return:            Encoded character
        """
        offset = self.position
        if self.right_rotor is not None:
            offset -= self.right_rotor.get_position()
        input_pin = (self.right_pins.index(character) + offset) % 26
        return self.left_pins[input_pin]

    def rotate(self):
        """Rotate the rotor one notch
        :return: Boolean so rotor to left will also rotate
        """
        rotate_left = self.right_pins[self.position] == self.notch
        self.position += 1
        self.position %= 26
        return rotate_left

    def is_rotor_reflector(self):
        return self.left_rotor is None
    
    def set_right(self, right_rotor):
        """Set up the rotor to the right"""
        self.right_rotor = right_rotor

    def set_left(self, left_rotor):
        """Set up the rotor to the left"""
        self.left_rotor = left_rotor

    def get_position(self):
        return self.position % 26

    def get_ring_setting(self):
        return self.ring_setting

    def is_notch_position(self):
        return self.right_pins[self.position] == self.notch

    def __str__(self):
        return self.Label

class EnigmaSetup:
    """The rotor, reflector and plugboard setup of the Enigma machine"""
    def __init__(self, reflector, rotors,  rotor_position, ring_setting, plugs):
        self.reflector = reflector
        self.rotors = rotors
        self.rotors_pos = rotor_position
        self.ring_settings = ring_setting
        self.plugs = plugs

    @classmethod
    def from_setup_string(cls, config_string):
        """Set the Enigma from an input string.
        For example "C I-II-III-IV 01-01-01-01 Z-Z-Z-Z AB-CD-EF-GH"
        is interpreted as:
            - Rotors from right to left: IV III, II, I, C
            - Rotor positions right to left: Z, Z, Z, Z
            - Ring setting right to left: 1, 1, 1, 1
            - Plugboard settings: AB, CD, EF, GH
        Plugboard setting are mandatory.
        :param config_string: An input configaration string
        :return: Instance of the configaration
        """

        config_parts = config_string.split()
        # get the name of the reflector
        config_reflector = config_parts[0]
        # get the list of the plugboard connection pairs if any defined
        if len(config_parts) > 4:
            config_plugboard = config_parts[4].replace('-', ' ').split()
        else:
            config_plugboard = []
        # get the rotor names, positions and ring settings in reverse order
        config_rotors = []
        config_positions = []
        config_ring_settings = []
        for rotor_label, ring_setting, rotor_position in zip(config_parts[1].split('-')[::-1],
                                                             config_parts[2].split('-')[::-1],
                                                             config_parts[3].split('-')[::-1]):
            config_rotors.append(rotor_label)
            config_positions.append(rotor_position)
            config_ring_settings.append(int(ring_setting))
        return cls(config_reflector, config_rotors, config_positions, config_ring_settings,  config_plugboard)

    def is_valid_setup(self):
        """Enigma settings verification"""

        lead_chars = set()
        if self.plugs:
            # Ensure no double connection on plugboard:
            for lead in self.plugs:
                for c in list(lead):
                    if c in lead_chars:
                        return False
                    else:
                        lead_chars.add(c)
        return True

    def __str__(self):
        """ Enigma settings will print out as follows:
        "C I-II-III-IV 7-11-15-19 Q-E-V-Z"
        """
        return "{0} {1} {2} {3} {4}".format(self.reflector,
                             "-".join(r for r in self.rotors[::-1]),
                             "-".join(str(r) for (r) in self.ring_settings[::-1]),
                             "-".join(r for r in self.rotors_pos[::-1]),
                             "-".join(r for r in self.plugs))

class Enigma:
    """Represents a 3 or 4 rotor Enigma encryption device"""

    def __init__(self, cnf):
        """Instantiate 3 or 4 rotor steckered or unsteckered Enigma from config
        :param cnf: An instance of EnigmaConfig class that
        specifies reflector, rotor and plugboard settings
        """

        self.config = cnf
        # apply plugboard configuration
        self.plugboard = Plugboard()
        for lead_config in cnf.plugs:
            self.plugboard.add(PlugLead(lead_config))

        # static input ring that connects to the right-most rotor
        self.input_ring = Rotor.Multiple_Rotors['Alpha']

        # apply rotor configuration, right to left 3 or 4 rotors
        # must be a either rotors: I, II, III, IV, V, Beta, Gammma
        self.rotors = list()
        for r_lbl, r_pos, r_ring in zip(cnf.rotors, cnf.rotors_pos, cnf.ring_settings):
            self.rotors.append(Rotor(r_lbl,
                                     pos=self.input_ring.index(r_pos),
                                     # ring settings should be 0-25 instead of 1-26
                                     ring=r_ring - 1))
        # at the end add the reflector (just a rotor that doesn't rotate)
        self.rotors.append(Rotor(cnf.reflector))
        # for each of the rotors set its neighbours to the left and to the right
        for rotor_inx in range(len(self.rotors)):
            first = rotor_inx == 0
            last = rotor_inx == len(self.rotors) - 1
            if not last:
                self.rotors[rotor_inx].set_left(self.rotors[rotor_inx + 1])
            if not first:
                self.rotors[rotor_inx].set_right(self.rotors[rotor_inx - 1])

    def encode_string(self, plain_text):
        """Encode or decode a string. Rotor position will not reset.
        :param plain_text: input plain or encrypted string
        :return: decoded or encoded string
        """

        encoded_string = ""
        for c in plain_text:
            encoded_string += str(self.encode_character(c))
        return encoded_string

    def rotate_n_steps(self, n):
        """Position rotors forward n-steps
        In case that encoding/decoding happens at an offset then this can be used
        to adjust the rotor positions.
        :param n: the number of steps to position rotors forward
        :return:
        """
        # rotate the rotors from right to left
        for i in range(n):
            rotate_left_rotor = self.rotors[0].rotate()
            if rotate_left_rotor or self.rotors[1].is_notch_position():
                rotate_left_rotor = self.rotors[1].rotate()
                if rotate_left_rotor:
                    self.rotors[2].rotate()

    def reset_rotors(self):
        """Set rotor positions back to initial position"""
        for r,p in zip(self.rotors[:-1],self.config.rotors_pos):
            r.position = self.input_ring.index(p)

    def encode_character(self, character):
        """Encode or decode a character through Enigma settings. 
        Will not reset the enigma settings.
        :param character: input character
        :return: decoded or encoded character
        """

        # swap character if connected in plugboard
        character = self.plugboard.encode(character)

        # rotate all the rotors
        self.rotate_n_steps(1)
        
        #pass characters
        for rotor in self.rotors:
            character = rotor.encode_right_to_left(character)
        for rotor in reversed(self.rotors[0:-1]):
            character = rotor.encode_left_to_right(character)

        # calculate offset between last rotor on right and static ring
        inx = self.input_ring.index(character)
        first_rotor_offset = (self.rotors[0].get_position()) % 26
        character = self.input_ring[(inx - first_rotor_offset) % 26]

        # swap the character again if connected in the plugboard by lead.
        character = self.plugboard.encode(character)
        return character

    def __str__(self):
        return str(self.config)

    def print_state(self):
        return "{0} {1} {2} {3} {4}".format(self.rotors[-1],
                                            "-".join(str(r) for r in self.rotors[-2::-1]),
                                            "-".join(str(r.ring_setting+1) for (r) in self.rotors[-2::-1]),
                                            "-".join(str(self.input_ring[r.position + r.ring_setting]) for r in self.rotors[-2::-1]),
                                            self.plugboard)
