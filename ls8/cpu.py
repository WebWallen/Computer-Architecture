import sys

class CPU:
    def __init__(self):
        # Preallocate 8 registers (arrays of binary numbers)
        self.reg = [0b0] * 8
        # Set up PC counter with 0 for now
        self.pc = 0
        # Need a RAM property for read and write function
        self.ram = [0b0] * 0xFF # FF (255) = largest number in 2 hex digits
        # Set up Instruction Register, assign None for now
        self.ir = None
        # Initialize stack pointer, subtract 1 from available registers
        self.sp = 8 - 1
        # When an interruption occurs, store the value in below address
        self.reg[self.sp] = 0xF4

        self.OPCODES = {
            # Add values in registers 1 + 2 and store sum in register #1
            0b10100000: 'ADD',
            # Call subroutine (function) at address stored in register
            0b01010000: 'CALL',
            # Halt CPU (exit the emulator)
            0b00000001: 'HLT',
            # Set value of register to integer
            0b10000010: 'LDI', 
            # Multiply values in registers 1 + 2 and store sum in register #1
            0b10100010: 'MUL',
            # Pop top stack value into register
            0b01000110: 'POP',
            # Push register value to the stack
            0b01000101: 'PUSH',
            # Print number stored in register
            0b01000111: 'PRN',
            # Return from subroutine
            0b00010001: 'RET',
            # Copy (store) value in register #2 to address stored in address #1
            0b10000100: 'ST'
    }
    
    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, val, address): 
        self.ram[address] = val

    # ALU means Arithmetic Logic Unit, performs all computations
    def alu(self, op, reg_a, reg_b):
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    # Helper function for ALU that stores right data and increments
    def alu_helper(self, op):
        # Command comes first, register A second
        reg_a = self.ram[self.pc + 1]
        # Register B comes third
        reg_b = self.ram[self.pc + 2]
        # Pass in the data to parent function
        self.alu(op, reg_a, reg_b)
        # Increment by three to account for command and 2 registers
        self.pc += 3

    # Call a subroutine located at address stored on register
    def call(self):
        # Command comes first, register address second
        reg_add = self.ram[self.pc + 1]
        # Return address follows command and register add
        ret_add = self.ram[self.pc + 2]
        # Decrement the register associated with this stack pointer
        self.reg[self.sp] -= 1
        # Assign the same pointer location to a value variable
        value = self.reg[self.sp]
        # Save the return address to the RAM location of our value
        self.ram[value] = ret_add
        # Store the appropriate register address a subroutine variable
        subroutine = self.reg[reg_add]
        # Assign the newly created subroutine variable to our PC
        self.pc = subroutine
    
    # Set register value to integer
    def ldi(self):
        # Command itself is first element, register comes second
        reg = self.ram[self.pc + 1]
        # Value is the third element, after command/register
        val = self.ram[self.pc + 2]
        # Assign the value to the correct[register]
        self.reg[reg] = val
        # Increment by three to reach next command
        self.pc += 3

    # Print value from register
    def prn(self):
        # Command itself is first value, register comes second
        reg = self.ram[self.pc + 1]
        # We are printing, not storing, so we just assign to reg
        val = self.reg[reg]
        # Print the value in both hex and decimal format
        print(f"Value: {val}")
        # Increment by 2 to reach the next command
        self.pc += 2

    # Push value from register, store on stack pointer
    def push(self):
        # Command comes first, register second
        reg = self.ram[self.pc + 1]
        # Assign value to appropriate register
        val = self.reg[reg]
        # Decrement the stack pointer by one
        self.reg[self.sp] -= 1
        # Store the value from register's stack pointer to RAM
        self.ram[self.reg[self.sp]] = val
        # Increment PC by 2 to reach our next command
        self.pc += 2

    # Pop top value from stack, store in register
    def pop(self):
        reg = self.ram[self.pc + 1]
        # Skip straight to storing the value (reverse of push)
        val = self.ram[self.reg[self.sp]]
        # Store value to the appropriate register
        self.reg[reg] = val
        # Increment the stack pointer by one
        self.reg[self.sp] += 1
        # Increment PC by 2 to reach our next command
        self.pc += 2

    # Return from a subroutine
    def ret(self):
        # Specify stack pointer in RAM as return address
        ret_add = self.ram[self.sp]
        # Increment register associated with pointer by 1
        self.reg[self.sp] += 1
        # Assign return address to the PC
        self.pc = ret_add

    # Copy the value on register B to address stored for register A
    def st(self):
        # Register A comes after the command
        reg_a = self.ram[self.pc + 1]
        # Register B comes after command and Reg A
        reg_b = self.ram[self.pc + 2]
        # Address A is stored on the first register
        add_a = self.reg[reg_a]
        # Value B is stored on the second register
        val_b = self.reg[reg_b]
        # Specify storage address (A) on RAM and assign value location (B)
        self.ram[add_a] = val_b
        self.pc += 2

    def load(self):
        address = 0
        program = sys.argv[1]
        with open(program) as file:
            for line in file:
                line = line.split("#")[0].strip()

                if line == '':
                    continue

                value = int(line, 2)
                self.ram[address] = value
                address += 1

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        # Initialize with Boolean so we can turn "On" and "Off"
        running = True
        # While the PC is running...
        while running:
            # Assign PC command stored in RAM to Instruction Register (IR)
            self.ir = self.ram[self.pc]
            try:
                # Create op and assign code attached to register
                op = self.OPCODES[self.ir]
                if op == 'ADD' or op == 'MUL' or op == 'SUB':
                    self.alu_helper(op)
                if op == 'CALL':
                    self.call()
                elif op == 'HLT':
                    running = False
                if op == 'LDI':
                    self.ldi()
                elif op == 'PRN': 
                    self.prn()
                elif op == 'PUSH':
                    self.push()
                elif op == 'POP':
                    self.pop()
                elif op == 'RET':
                    self.ret()
                elif op == 'ST':
                    self.st()
            except KeyError:
                print(f"{self.ir} is not a valid command")
                self.pc += 1
        pass