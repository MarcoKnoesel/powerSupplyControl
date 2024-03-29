import streamlit as st

class Messages:
	def __init__(self):
		self.errors = []
		self.warnings = []
		self.info = []
		self.isUpdated = False

	def newError(self, message: str) -> None:
		self.errors.append(message)
		self.isUpdated = True

	def newWarning(self, message: str) -> None:
		self.errors.append(message)
		self.isUpdated = True

	def newInfo(self, message: str) -> None:
		self.errors.append(message)
		self.isUpdated = True

	def print(self) -> None:
		for message in self.errors:
			st.error(message, icon = "❗")
		for message in self.warnings:
			st.error(message, icon = "⚠️")
		for message in self.info:
			st.error(message, icon = "ℹ️")
		self.errors.clear()
		self.warnings.clear()
		self.info.clear()
		self.isUpdated = False