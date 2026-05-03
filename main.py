async def setup_hook(self):
    # Najpierw czyścimy stare komendy (pusta synchronizacja)
    self.tree.clear(guild=MY_GUILD)
    await self.tree.sync(guild=MY_GUILD)

    # Teraz dodajemy je od nowa
    self.tree.copy_from_slash_command(test_wifi)
    self.tree.copy_from_slash_command(pomoc)
    await self.tree.sync(guild=MY_GUILD)
    print("Baza danych komend została CAŁKOWICIE odświeżona!")
