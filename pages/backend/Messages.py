import streamlit as st

class Messages:
	def __init__(self):
		self.errors = []
		self.warnings = []
		self.info = []
		self.isUpdated = False
		self.tooManyMessagesErrorWasSent = False

	# create a new error message
	def newError(self, message: str) -> None:
		if not self.tooManyMessages():
			self.errors.append(message)
			self.isUpdated = True

	# create a new warning message
	def newWarning(self, message: str) -> None:
		if not self.tooManyMessages():
			self.warnings.append(message)
			self.isUpdated = True

	# create a new inforamtion message
	def newInfo(self, message: str) -> None:
		if not self.tooManyMessages():
			self.info.append(message)
			self.isUpdated = True

	# Check if too many messages have been created.
	# If the limit was exceeded with the most recent message,
	# create one last error message, saying there were too many messages.
	def tooManyMessages(self) -> bool:
		nMessages = len(self.errors) + len(self.warnings) + len(self.info)
		if nMessages >= 30:
			self.sendTooManyMessagesError()
			return True
		return False
		
	# Create an error message saying there were too many messages created.
	# After that, it's not possible to create more messages,
	# until self.print() is invoked.
	def sendTooManyMessagesError(self) -> None:
		if not self.tooManyMessagesErrorWasSent:
			self.errors.append("Too many error, warning or information messages. Drop the remaining ones.")
			self.isUpdated = True
			self.tooManyMessagesErrorWasSent = True

	# print all messages and reset everything
	def print(self) -> None:
		for message in self.errors:
			st.error(message, icon = "❗")
		for message in self.warnings:
			st.warning(message, icon = "⚠️")
		for message in self.info:
			st.info(message, icon = "ℹ️")
		self.errors.clear()
		self.warnings.clear()
		self.info.clear()
		self.isUpdated = False
		self.tooManyMessagesErrorWasSent = False