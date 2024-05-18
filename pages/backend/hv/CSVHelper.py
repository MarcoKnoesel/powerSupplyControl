def isComment(line: str) -> bool:
	for i in range(0, len(line)):
		c = line[i]
		#  ignore whitespaces
		if c != " " and c != "\t" and c != "\n":
			# check the first non-whitespace character
			if c == "#":
				return True
			else:
				return False
	# for empty lines or lines with whitespaces only: return True
	return True



def findPosOfCharInString(char: str, string: str):
	# only allow searching for single characters
	if len(char) != 1:
		return None
	positions = []
	for i in range(0, len(string)):
		if string[i] == char:
			positions.append(i)
	# char not found
	if len(positions) == 0:
		return None
	# return all positions of char
	return positions



def getEntry(line: str, commaPositions, iEntry: int) -> str:
	if iEntry == 0:
		return line[0 : commaPositions[0]]
	if iEntry == len(commaPositions):
		return line[commaPositions[iEntry - 1] + 1 : ]
	return line[commaPositions[iEntry - 1] + 1 : commaPositions[iEntry]]