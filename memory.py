import sys

# Assigning basic operations to reference numbers
PRINT_BEEJ              = 1
HALT                    = 2
PRINT_NUM               = 3
SAVE                    = 4     # Save value to register
PRINT_REGISTER          = 5     # Print value in register
ADD                     = 6     # Add 2 registers, store result in 1st

# Memory is contained in an array-like structure as seen here
memory = [
    PRINT_BEEJ,
    SAVE,            # Save 65 in R2
    65,
    2,
    SAVE,            # Save 20 in R3
    20,
    3,
    ADD,             # Add R2 and R3
    2,
    3,
    PRINT_REGISTER,  # Print R2 (sum R2 + R3 = 85)
    2,
    HALT             # Stop
]

# Preallocate a register (faster way of deploying CPU operations)
register = [0] * 8

# Initialize program counter (pc) and set to 0
pc = 0

# While there is stuff loading in memory...
while True:
    # Specify the PC command we want from memory array
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