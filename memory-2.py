import sys

# Assigning basic operations to reference numbers
PRINT_BEEJ              = 1
HALT                    = 2
PRINT_NUM               = 3
SAVE                    = 4     # Save value to register
PRINT_REGISTER          = 5     # Print value in register
ADD                     = 6     # Add 2 registers, store result in 1st

# Difference = using load function and preallocating memory
memory = [0] * 256

register = [0] * 8

pc = 0 

def load_memory(filename):
    try:  
        address = 0
        # Open the file
        with open(filename) as f:
            # Read all the lines
            for line in f:
                # Parse out comments
                comment_split = line.strip().split('#')
                # Cast the numbers from strings to ints
                value = comment_split[0].strip()
                # Ignore blank lines
                if value == "":
                    continue
                # Assign integer of value to num
                num = int(value)
                # Attach num to appropriate memory address
                memory[address] = num
                # Increment address 
                address += 1
    # If file is not found
    except FileNotFoundError:
        print("File not found")
        sys.exit(2)

# Error handling for system input/arg
if len(sys.argv) != 2:
    print("You forgot the file name")
    sys.exit(1)

# Load memory with the file specified
load_memory(sys.argv[1])
# Print what's stored in memory
print(memory)

# While there are commands left to do
while True:
    # Assign memory's program counter to command
    command = memory[pc]
    # Set up conditional statements for each command/outcome
    if command == PRINT_BEEJ:
        # Only one part in memory
        print("Beej!")
        pc += 1
    # Print number without saving to storage 
    elif command == PRINT_NUM:
        # Two parts in memory -- num is the second one
        num = memory[pc + 1]
        print(num)
        # Skip ahead two to reach next PC command
        pc += 2
    # Save value to a register
    elif command == SAVE:
        # Three parts in memory -- num is second
        num = memory[pc + 1]
        # Register is third part of memory
        reg = memory[pc + 2]
        # Assign num to the right register
        register[reg] = num
        # Skip ahead three to reach next 
        pc += 3
    # Print the value inside a register
    elif command == PRINT_REGISTER: 
        # Two parts in memory -- reg is second
        reg = memory[pc + 1]
        # Print the info contained within register
        print(register[reg])
        # Skip ahead two to reach the next command
        pc += 2
    # Combine the values in two different registers
    elif command == ADD:
        # Three parts in memory -- registers are 2/3
        reg_a = memory[pc + 1]
        reg_b = memory[pc + 2]
        # Add the two registers together, assign to first
        register[reg_a] += register[reg_b]
        # Skip ahead three to reach the next/final command
        pc += 3
    # Cease all operations
    elif command == HALT:
        sys.exit(0)
    # Error handling
    else:
        print(f"{command} is not a valid command.")
        sys.exit(1)