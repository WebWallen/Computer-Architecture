import sys

# *** First, specify the address of each command/operation so they can be accessed by the CPU ***

# Add values in registers 1 + 2 and store sum in register #1
ADD = 0b10100000
# Call subroutine (function) at address stored in register
CALL = 0b01010000
# Compare the values stored in two registers
CMP = 0b10100111
# Halt CPU (exit the emulator)
HLT = 0b00000001
# If equal flag is set (true), jump to address stored in register
JEQ = 0b01010101
# Jump to the address stored in register
JMP = 0b01010100
# If not equal (false), jump to address stored in register
JNE = 0b01010110
# Set value of register to integer
LDI = 0b10000010 
# Multiply values in registers 1 + 2 and store sum in register #1
MUL = 0b10100010
# Pop top stack value into register
POP = 0b01000110
# Push register value to the stack
PUSH = 0b01000101
# Print number stored in register
PRN = 0b01000111
# Return from subroutine
RET = 0b00010001
# Copy (store) value in register #2 to address stored in address #1
ST = 0b10000100

# *** Second, initialize the CPU class with: registers, RAM, instruction register, program counter, stack pointer, and flag ***

class CPU:
    def __init__(self):
        # Preallocate 8 registers (arrays of binary numbers)
        self.reg = [0b0] * 8
        # Need a random access memory property to be used with the read and write function
        self.ram = [0b0] * 256
        # Set up Instruction Register -- command currently being excuted -- and assign None for now
        self.ir = None
        # Initialize the program counter, which contains address to the current instruction
        self.pc = 0
        # Create a stack pointer, which indicates location of last item put on the stack, and subtract 1 from available registers
        self.sp = 8 - 1
        # Adding a flag register to track jump, equal, and not equal commands
        self.fl = [0b0] * 8

# *** Third, set up a dispatch table containing pointers to functions associated with each instruction name: achieves O(1) ***

        # Dispatch Table (contains pointers to the functions associated with each command)
        self.dispatch = {
            ADD: self.add,
            CALL: self.call,
            CMP: self.cmp,
            JEQ: self.jeq,
            JNE: self.jne,
            JMP: self.jmp,
            LDI: self.ldi,
            MUL: self.mul,
            POP: self.pop,
            PUSH: self.push,
            PRN: self.prn,
            RET: self.ret,
            ST: self.st
        }

# *** Fourth, write the functional logic for each part of our program (start with ALU and the five functions assocaited with it) ***

    # ALU means Arithmetic Logic Unit, performs all computations (eliminated helper function as it became obselete with dispatch table)
    def alu(self, op, reg_a, reg_b):
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
        # Has three flags: greater (0), less (1), equal (2)
            self.fl[0] = 0 
            self.fl[1] = 0
            self.fl[2] = 0
            # If first value is greater than second
            if self.reg[reg_a] > self.reg[reg_b]:
                # Set appropriate register (0) to true (1)
                self.fl[0] = 1
            # If the first value is less than the second
            if self.reg[reg_a] < self.reg[reg_b]:
                # Set appropriate register (1) to true (1)
                self.fl[1] = 1
            # Otherwise (the values are equal)
            else:
                # Set appropriate register (2) to true (1)
                self.fl[2] = 1
        elif op == "JEQ":
            # If the "equal" flag (2) is set to 1 (true)
            if self.fl[2] == 1:
                # Jump to that register
                self.jmp(reg_a, reg_b)
            else:
                # Increment counter (accounting for both registers)
                self.pc += 2
        elif op == "JNE":
            # If the "equal" flag (2) is set to 0 (false)
            if self.fl[2] == 0:
                # Jump to that register
                self.jmp(reg_a, reg_b)
            else: 
                # Increment counter (accounting for both registers)
                self.pc += 2
        else:
            raise Exception("Unsupported ALU operation")

    # Need to explicitly define this now due to the use of dispatch table
    def add(self, op_a, op_b):
        self.alu("ADD", op_a, op_b)
        # Increment must account for command and both registers
        self.pc += 3

    # Same as comment above
    def mul(self, op_a, op_b):
        self.alu("MUL", op_a, op_b)
        self.pc += 3

    # Compare the two values (a, b) and increment by three
    def cmp(self, op_a, op_b):
        self.alu("CMP", op_a, op_b)
        self.pc += 3

    # If equal (true), jump to the address (increment handled in ALU)
    def jeq(self, op_a, op_b):
        self.alu("JEQ", op_a, op_b)

    # If not equal (false), jump to the address (ditto ^)
    def jne(self, op_a, op_b):
        self.alu("JNE", op_a, op_b)

    # Set PC to address stored in given register
    def jmp(self, op_a, op_b):
        self.pc = self.reg[op_a]
    
    # Call a subroutine located at address stored on register
    def call(self, op_a, op_b):
        # Assign return address (2 ahead of commnd)
        ret_add = self.pc + 2
        # Decrement the stack pointer of register
        self.reg[self.sp] -= 1
        # Attach ^ to RAM and set it equal to return address -- RAM holds register and register holds stack pointer
        self.ram[self.reg[self.sp]] = ret_add
        # Assign op A register to the PC
        self.pc = self.reg[op_a] # This = performance of subroutine

    # Return from a subroutine
    def ret(self, op_a, op_b):
        # Attach SP to register and register to RAM, then assign to ret_add (reverse of call)
        ret_add = self.ram[self.reg[self.sp]]
        # Increment register associated with pointer by 1 (notice the net result of 0 when combined with decrement above)
        self.reg[self.sp] += 1
        # Assign return address to the PC
        self.pc = ret_add # This = exiting from the subroutine

    # Set register value (A) to integer (B)
    def ldi(self, op_a, op_b):
        self.reg[op_a] = op_b
        # Increment by 3 to reach the next command
        self.pc += 3

    # Print value from register
    def prn(self, op_a, op_b):
        # Print value attached to first operation in register
        print(self.reg[op_a])
        # Increment by 2 to reach the next command
        self.pc += 2

    # Push value from register, store on stack pointer
    def push(self, op_a, op_b):
        # Decrement the stack pointer
        self.sp -= 1
        # Assign value on register (A) to the stack pointer stored in RAM
        self.ram[self.sp] = self.reg[op_a]
        # Increment +2 to reach next command
        self.pc += 2

    # Pop top value from stack, store in register
    def pop(self, op_a, op_b):
        # Increment the stack pointer
        self.sp += 1
        # Assign the stack pointer stored in RAM to value on register (A) -- reverse of push
        self.reg[op_a] = self.ram[self.sp]
        # Increment +2 to reach next command
        self.pc += 2

    # Copy the value on register B to address stored for register A
    def st(self, op_a, op_b):
        self.reg[op_a] = self.reg[op_b]
        # Increment +2 for next command
        self.pc += 2

    # Fetch the address of instruction stored on RAM
    def ram_read(self, address):
        return self.ram[address]

    # Store (write) the value attached to address on RAM
    def ram_write(self, val, address): 
        self.ram[address] = val
    
    # Load the information contained within a command
    def load(self):
        address = 0
        # Program -- ls8.py -- is first argument after python
        program = sys.argv[1]
        # When the program opens a file...
        with open(program) as file:
            # For each line in the file...
            for line in file:
                # Remove any lines that [start] with a comment
                line = line.split("#")[0].strip()
                # If the line contains no relevant data (empty string)...
                if line == '':
                    # Continue to the next line
                    continue
                # Convert the line to a binary (, 2) number and assign to value
                value = int(line, 2)
                # Store (assign) the value to the address contained in RAM
                self.ram[address] = value
                # Increment to the next instruction/command address
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
        # Initialize with Boolean so we can turn "On" (True) and "Off" (False)
        running = True
        # While the program is running...
        while running:
            # Assign PC command stored in RAM to Instruction Register (IR)
            ir = self.ram[self.pc]
            # Assign first PC address after command (typically value) to operand A
            op_a = self.ram_read(self.pc + 1)
            # Assign second PC address after command (typically register) to operand B
            op_b = self.ram_read(self.pc + 2)
            # If the PC command is HLT (halt), turn the program off
            if ir == HLT:
                running = False
            # Otherwise, select the instruction register from dispatch table and pass in the operators
            else:
                self.dispatch[ir](op_a, op_b)