import unittest
from dao import Dao, RegionNotFoundException, InvalidRegionsException, \
    InvalidNameException, DuplicateAliasException, DuplicateUsernameException, \
    UpdateTournamentException, gen_password, verify_password
from bson.objectid import ObjectId
from ConfigParser import ConfigParser
from model import *
from ming import mim
import trueskill
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient

DATABASE_NAME = 'garpr_test'
CONFIG_LOCATION = 'config/config.ini'

class TestDAO(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        config = ConfigParser()
        config.read(CONFIG_LOCATION)
        username = config.get('database', 'user')
        host = config.get('database', 'host')
        auth_db = config.get('database', 'auth_db')
        password = config.get('database', 'password')
        self.mongo_client = MongoClient(host='mongodb://%s:%s@%s/%s' % (username, password, host, auth_db))
        self.mongo_client.drop_database(DATABASE_NAME)

    def setUp(self):

        self.player_1_id = ObjectId()
        self.player_2_id = ObjectId()
        self.player_3_id = ObjectId()
        self.player_4_id = ObjectId()
        self.player_5_id = ObjectId()
        self.player_1 = Player(
                'gaR',
                ['gar', 'garr'],
                {'norcal': TrueskillRating(), 'texas': TrueskillRating()},
                ['norcal', 'texas'],
                id=self.player_1_id)
        self.player_2 = Player(
                'sfat',
                ['sfat', 'miom | sfat'],
                {'norcal': TrueskillRating()},
                ['norcal'],
                id=self.player_2_id)
        self.player_3 = Player(
                'mango',
                ['mango', 'gar'],
                {'norcal': TrueskillRating(trueskill_rating=trueskill.Rating(mu=2, sigma=3))},
                ['socal'],
                id=self.player_3_id)
        self.player_4 = Player('shroomed', ['shroomed'], {'norcal': TrueskillRating()}, ['norcal'], id=self.player_4_id)
        self.player_5 = Player('pewpewu', ['pewpewu'], {'norcal': TrueskillRating()}, ['norcal', 'socal'], id=self.player_5_id)

        # only includes players 1-3
        self.players = [self.player_1, self.player_2, self.player_3]

        self.tournament_id_1 = ObjectId()
        self.tournament_type_1 = 'tio'
        self.tournament_raw_1 = 'raw1'
        self.tournament_date_1 = datetime(2013, 10, 16)
        self.tournament_name_1 = 'tournament 1'
        self.tournament_players_1 = [self.player_1_id, self.player_2_id, self.player_3_id, self.player_4_id]
        self.tournament_matches_1 = [
                MatchResult(winner=self.player_1_id, loser=self.player_2_id),
                MatchResult(winner=self.player_3_id, loser=self.player_4_id)
        ]
        self.tournament_regions_1 = ['norcal']

        # tournament 2 is earlier than tournament 1, but inserted after
        self.tournament_id_2 = ObjectId()
        self.tournament_type_2 = 'challonge'
        self.tournament_raw_2 = 'raw2'
        self.tournament_date_2 = datetime(2013, 10, 10)
        self.tournament_name_2 = 'tournament 2'
        self.tournament_players_2 = [self.player_5_id, self.player_2_id, self.player_3_id, self.player_4_id]
        self.tournament_matches_2 = [
                MatchResult(winner=self.player_5_id, loser=self.player_2_id),
                MatchResult(winner=self.player_3_id, loser=self.player_4_id)
        ]
        self.tournament_regions_2 = ['norcal', 'texas']

        self.tournament_1 = Tournament(self.tournament_type_1,
                                       self.tournament_raw_1,
                                       self.tournament_date_1,
                                       self.tournament_name_1,
                                       self.tournament_players_1,
                                       self.tournament_matches_1,
                                       self.tournament_regions_1,
                                       id=self.tournament_id_1)

        self.tournament_2 = Tournament(self.tournament_type_2,
                                       self.tournament_raw_2,
                                       self.tournament_date_2,
                                       self.tournament_name_2,
                                       self.tournament_players_2,
                                       self.tournament_matches_2,
                                       self.tournament_regions_2,
                                       id=self.tournament_id_2)

        self.tournament_ids = [self.tournament_id_1, self.tournament_id_2]
        self.tournaments = [self.tournament_1, self.tournament_2]

        self.pending_tournament_id_1 = ObjectId()
        self.pending_tournament_type_1 = 'tio'
        self.pending_tournament_raw_1 = 'raw1'
        self.pending_tournament_date_1 = datetime(2013, 10, 11)
        self.pending_tournament_name_1 = 'pending tournament 1'
        self.pending_tournament_players_1 = [self.player_1.name, self.player_2.name, self.player_3.name, self.player_4.name]
        self.pending_tournament_matches_1 = [
                MatchResult(winner=self.player_1.name, loser=self.player_2.name),
                MatchResult(winner=self.player_3.name, loser=self.player_4.name)
        ]
        self.pending_tournament_regions_1 = ['norcal']

        self.pending_tournament_1 = PendingTournament(self.pending_tournament_type_1,
                                                      self.pending_tournament_raw_1,
                                                      self.pending_tournament_date_1,
                                                      self.pending_tournament_name_1,
                                                      self.pending_tournament_players_1,
                                                      self.pending_tournament_matches_1,
                                                      self.pending_tournament_regions_1,
                                                      id=self.pending_tournament_id_1)

        self.pending_tournaments = [self.pending_tournament_1]

        self.ranking_entry_1 = RankingEntry(1, self.player_1_id, 20)
        self.ranking_entry_2 = RankingEntry(2, self.player_2_id, 19)
        self.ranking_entry_3 = RankingEntry(3, self.player_3_id, 17.5)
        self.ranking_entry_4 = RankingEntry(3, self.player_4_id, 16.5)

        self.ranking_time_1 = datetime(2013, 4, 20)
        self.ranking_time_2 = datetime(2013, 4, 21)
        self.ranking_1 = Ranking('norcal', self.ranking_time_1, self.tournament_ids,
                                 [self.ranking_entry_1, self.ranking_entry_2, self.ranking_entry_3])
        self.ranking_2 = Ranking('norcal', self.ranking_time_2, self.tournament_ids,
                                 [self.ranking_entry_1, self.ranking_entry_2, self.ranking_entry_4])
        self.ranking_3 = Ranking('texas', self.ranking_time_2, self.tournament_ids,
                                 [self.ranking_entry_1, self.ranking_entry_2])

        self.rankings = [self.ranking_1, self.ranking_2, self.ranking_3]

        self.user_id_1 = 'abc123'
        self.user_admin_regions_1 = ['norcal', 'texas']
        self.user_1 = User(self.user_id_1, self.user_admin_regions_1, 'user1', 0,0)

        self.user_id_2 = 'asdfasdf'
        self.user_full_name_2 = 'Full Name'
        self.user_admin_regions_2 = []
        self.user_2 = User(self.user_id_2, self.user_admin_regions_2, self.user_full_name_2 , 0, 0)

        self.users = [self.user_1, self.user_2]

        self.region_1 = Region('norcal', 'Norcal')
        self.region_2 = Region('texas', 'Texas')

        self.regions = [self.region_1, self.region_2]

        for region in self.regions:
            Dao.insert_region(region, self.mongo_client, database_name=DATABASE_NAME)

        self.norcal_dao = Dao('norcal', self.mongo_client, database_name=DATABASE_NAME)

        for player in self.players:
            self.norcal_dao.insert_player(player)

        for tournament in self.tournaments:
            self.norcal_dao.insert_tournament(tournament)

        for pending_tournament in self.pending_tournaments:
            self.norcal_dao.insert_pending_tournament(pending_tournament)

        for ranking in self.rankings:
            self.norcal_dao.insert_ranking(ranking)

        for user in self.users:
            self.norcal_dao.insert_user(user)

    def tearDown(self):
        self.mongo_client.drop_database(DATABASE_NAME)

    def test_init_with_invalid_region(self):
        # create a dao with an existing region
        Dao('norcal', self.mongo_client, database_name=DATABASE_NAME)

        # create a dao with a new region
        with self.assertRaises(RegionNotFoundException):
            Dao('newregion', self.mongo_client, database_name=DATABASE_NAME)

    def test_get_all_regions(self):
        # add another region
        region = Region('newregion', 'New Region')
        Dao.insert_region(region, self.mongo_client, database_name=DATABASE_NAME)

        regions = Dao.get_all_regions(self.mongo_client, database_name=DATABASE_NAME)
        self.assertEquals(len(regions), 3)
        self.assertEquals(regions[0], region)
        self.assertEquals(regions[1], self.region_1)
        self.assertEquals(regions[2], self.region_2)

    def test_get_player_by_id(self):
        self.assertEquals(self.norcal_dao.get_player_by_id(self.player_1_id), self.player_1)
        self.assertEquals(self.norcal_dao.get_player_by_id(self.player_2_id), self.player_2)
        self.assertEquals(self.norcal_dao.get_player_by_id(self.player_3_id), self.player_3)
        self.assertIsNone(self.norcal_dao.get_player_by_id(ObjectId()))

    def test_get_player_by_alias(self):
        self.assertEquals(self.norcal_dao.get_player_by_alias('gar'), self.player_1)
        self.assertEquals(self.norcal_dao.get_player_by_alias('GAR'), self.player_1)
        self.assertEquals(self.norcal_dao.get_player_by_alias('garr'), self.player_1)
        self.assertEquals(self.norcal_dao.get_player_by_alias('sfat'), self.player_2)
        self.assertEquals(self.norcal_dao.get_player_by_alias('miom | sfat'), self.player_2)

        self.assertIsNone(self.norcal_dao.get_player_by_alias('mango'))
        self.assertIsNone(self.norcal_dao.get_player_by_alias('miom|sfat'))
        self.assertIsNone(self.norcal_dao.get_player_by_alias(''))

    def test_get_players_by_alias_from_all_regions(self):
        self.assertEquals(self.norcal_dao.get_players_by_alias_from_all_regions('gar'), [self.player_1, self.player_3])
        self.assertEquals(self.norcal_dao.get_players_by_alias_from_all_regions('GAR'), [self.player_1, self.player_3])
        self.assertEquals(self.norcal_dao.get_players_by_alias_from_all_regions('garr'), [self.player_1])
        self.assertEquals(self.norcal_dao.get_players_by_alias_from_all_regions('sfat'), [self.player_2])
        self.assertEquals(self.norcal_dao.get_players_by_alias_from_all_regions('miom | sfat'), [self.player_2])
        self.assertEquals(self.norcal_dao.get_players_by_alias_from_all_regions('mango'), [self.player_3])

        self.assertEquals(self.norcal_dao.get_players_by_alias_from_all_regions('miom|sfat'), [])
        self.assertEquals(self.norcal_dao.get_players_by_alias_from_all_regions(''), [])

    def test_get_player_id_map_from_player_aliases(self):
        aliases = ['GAR', 'sfat', 'asdf', 'mango']
        expected_map = [
            {'player_alias': 'GAR', 'player_id': self.player_1_id},
            {'player_alias': 'sfat', 'player_id': self.player_2_id},
            {'player_alias': 'asdf', 'player_id': None},
            {'player_alias': 'mango', 'player_id': None},
        ]
        map = self.norcal_dao.get_player_id_map_from_player_aliases(aliases)
        self.assertEquals(map, expected_map)

    def test_get_all_players(self):
        self.assertEquals(self.norcal_dao.get_all_players(), [self.player_1, self.player_2])

    def test_get_all_players_all_regions(self):
        self.assertEquals(self.norcal_dao.get_all_players(all_regions=True), [self.player_1, self.player_3, self.player_2])

    def test_add_player_duplicate(self):
        with self.assertRaises(DuplicateKeyError):
            self.norcal_dao.insert_player(self.player_1)

    def test_delete_player(self):
        self.assertEquals(self.norcal_dao.get_player_by_id(self.player_1_id), self.player_1)
        self.assertEquals(self.norcal_dao.get_player_by_id(self.player_2_id), self.player_2)
        self.assertEquals(self.norcal_dao.get_player_by_id(self.player_3_id), self.player_3)

        self.norcal_dao.delete_player(self.player_2)
        self.assertEquals(self.norcal_dao.get_player_by_id(self.player_1_id), self.player_1)
        self.assertIsNone(self.norcal_dao.get_player_by_id(self.player_2_id))
        self.assertEquals(self.norcal_dao.get_player_by_id(self.player_3_id), self.player_3)

        self.norcal_dao.delete_player(self.player_3)
        self.assertEquals(self.norcal_dao.get_player_by_id(self.player_1_id), self.player_1)
        self.assertIsNone(self.norcal_dao.get_player_by_id(self.player_2_id))
        self.assertIsNone(self.norcal_dao.get_player_by_id(self.player_3_id))

        self.norcal_dao.delete_player(self.player_1)
        self.assertIsNone(self.norcal_dao.get_player_by_id(self.player_1_id))
        self.assertIsNone(self.norcal_dao.get_player_by_id(self.player_2_id))
        self.assertIsNone(self.norcal_dao.get_player_by_id(self.player_3_id))

    def test_update_player(self):
        self.assertEquals(self.norcal_dao.get_player_by_id(self.player_1_id), self.player_1)
        self.assertEquals(self.norcal_dao.get_player_by_id(self.player_2_id), self.player_2)
        self.assertEquals(self.norcal_dao.get_player_by_id(self.player_3_id), self.player_3)

        player_1_clone = Player(
                'gaR',
                ['gar', 'garr'],
                {'norcal': TrueskillRating(), 'texas': TrueskillRating()},
                ['norcal', 'texas'],
                id=self.player_1_id)
        player_1_clone.name = 'garrr'
        player_1_clone.aliases.append('garrr')
        del player_1_clone.ratings['texas']
        self.assertNotEquals(self.norcal_dao.get_player_by_id(self.player_1_id), player_1_clone)

        self.norcal_dao.update_player(player_1_clone)

        self.assertNotEquals(self.norcal_dao.get_player_by_id(self.player_1_id), self.player_1)
        self.assertEquals(self.norcal_dao.get_player_by_id(self.player_2_id), self.player_2)
        self.assertEquals(self.norcal_dao.get_player_by_id(self.player_3_id), self.player_3)
        self.assertEquals(self.norcal_dao.get_player_by_id(self.player_1_id), player_1_clone)

    def test_add_alias_to_player(self):
        new_alias = 'gaRRR'
        lowercase_alias = 'garrr'
        old_expected_aliases = ['gar', 'garr']
        new_expected_aliases = ['gar', 'garr', 'garrr']

        self.assertEquals(self.norcal_dao.get_player_by_id(self.player_1_id).aliases, old_expected_aliases)
        self.assertEquals(self.player_1.aliases, old_expected_aliases)
        self.norcal_dao.add_alias_to_player(self.player_1, new_alias)
        self.assertEquals(self.norcal_dao.get_player_by_id(self.player_1_id).aliases, new_expected_aliases)
        self.assertEquals(self.player_1.aliases, new_expected_aliases)

    def test_add_alias_to_player_duplicate(self):
        with self.assertRaises(DuplicateAliasException):
            self.norcal_dao.add_alias_to_player(self.player_1, 'garr')

    def test_update_player_name(self):
        self.assertEquals(self.norcal_dao.get_player_by_id(self.player_1_id).name, 'gaR')
        self.assertEquals(self.player_1.name, 'gaR')
        self.norcal_dao.update_player_name(self.player_1, 'gaRR')
        self.assertEquals(self.norcal_dao.get_player_by_id(self.player_1_id).name, 'gaRR')
        self.assertEquals(self.player_1.name, 'gaRR')

    def test_update_player_name_non_alias(self):
        with self.assertRaises(InvalidNameException):
            self.norcal_dao.update_player_name(self.player_1, 'asdf')

    def test_update_pending_tournament(self):
        pending_tournament_1 = self.norcal_dao.get_pending_tournament_by_id(self.pending_tournament_id_1)
        self.assertEquals(pending_tournament_1.id, self.pending_tournament_id_1)
        self.assertEquals(pending_tournament_1.type, self.pending_tournament_type_1)
        self.assertEquals(pending_tournament_1.raw, self.pending_tournament_raw_1)
        self.assertEquals(pending_tournament_1.date, self.pending_tournament_date_1)
        self.assertEquals(pending_tournament_1.name, self.pending_tournament_name_1)
        self.assertEquals(pending_tournament_1.matches, self.pending_tournament_matches_1)
        self.assertEquals(pending_tournament_1.players, self.pending_tournament_players_1)
        self.assertEquals(pending_tournament_1.regions, self.pending_tournament_regions_1)

        pending_tournament_1_raw_new = 'asdfasdf'
        pending_tournament_1_name_new = 'new pending tournament name'

        pending_tournament_1.raw = pending_tournament_1_raw_new
        pending_tournament_1.name = pending_tournament_1_name_new

        self.norcal_dao.update_pending_tournament(pending_tournament_1)

        pending_tournament_1 = self.norcal_dao.get_pending_tournament_by_id(self.pending_tournament_id_1)
        self.assertEquals(pending_tournament_1.id, self.pending_tournament_id_1)
        self.assertEquals(pending_tournament_1.type, self.pending_tournament_type_1)
        self.assertEquals(pending_tournament_1.raw, pending_tournament_1_raw_new)
        self.assertEquals(pending_tournament_1.date, self.pending_tournament_date_1)
        self.assertEquals(pending_tournament_1.name, pending_tournament_1_name_new)
        self.assertEquals(pending_tournament_1.matches, self.pending_tournament_matches_1)
        self.assertEquals(pending_tournament_1.players, self.pending_tournament_players_1)
        self.assertEquals(pending_tournament_1.regions, self.pending_tournament_regions_1)

    def test_update_pending_tournament_empty_raw(self):
        pending_tournament = self.norcal_dao.get_pending_tournament_by_id(self.pending_tournament_id_1)
        pending_tournament.raw = ''

        with self.assertRaises(UpdateTournamentException):
            self.norcal_dao.update_tournament(pending_tournament)

    def test_get_all_pending_tournaments(self):
        pending_tournaments = self.norcal_dao.get_all_pending_tournaments()

        self.assertEquals(len(pending_tournaments), 1)

        pending_tournament = pending_tournaments[0]
        self.assertEquals(pending_tournament.id, self.pending_tournament_id_1)
        self.assertEquals(pending_tournament.type, self.pending_tournament_type_1)
        self.assertEquals(pending_tournament.raw, '')
        self.assertEquals(pending_tournament.date, self.pending_tournament_date_1)
        self.assertEquals(pending_tournament.name, self.pending_tournament_name_1)
        self.assertEquals(pending_tournament.matches, self.pending_tournament_matches_1)
        self.assertEquals(pending_tournament.players, self.pending_tournament_players_1)
        self.assertEquals(pending_tournament.regions, self.pending_tournament_regions_1)

    def test_get_all_pending_tournaments_for_region(self):
        pending_tournaments = self.norcal_dao.get_all_pending_tournaments(regions=['norcal'])

        self.assertEquals(len(pending_tournaments), 1)

        pending_tournament = pending_tournaments[0]
        self.assertEquals(pending_tournament.id, self.pending_tournament_id_1)
        self.assertEquals(pending_tournament.type, self.pending_tournament_type_1)
        self.assertEquals(pending_tournament.raw, '')
        self.assertEquals(pending_tournament.date, self.pending_tournament_date_1)
        self.assertEquals(pending_tournament.name, self.pending_tournament_name_1)
        self.assertEquals(pending_tournament.matches, self.pending_tournament_matches_1)
        self.assertEquals(pending_tournament.players, self.pending_tournament_players_1)
        self.assertEquals(pending_tournament.regions, self.pending_tournament_regions_1)

    def test_get_pending_tournament_by_id(self):
        pending_tournament = self.norcal_dao.get_pending_tournament_by_id(self.pending_tournament_id_1)
        self.assertEquals(pending_tournament.id, self.pending_tournament_id_1)
        self.assertEquals(pending_tournament.type, self.pending_tournament_type_1)
        self.assertEquals(pending_tournament.raw, self.pending_tournament_raw_1)
        self.assertEquals(pending_tournament.date, self.pending_tournament_date_1)
        self.assertEquals(pending_tournament.name, self.pending_tournament_name_1)
        self.assertEquals(pending_tournament.matches, self.pending_tournament_matches_1)
        self.assertEquals(pending_tournament.players, self.pending_tournament_players_1)
        self.assertEquals(pending_tournament.regions, self.pending_tournament_regions_1)

        self.assertIsNone(self.norcal_dao.get_tournament_by_id(ObjectId()))

    def test_delete_pending_tournament(self):
        pending_tournament = self.norcal_dao.get_pending_tournament_by_id(self.pending_tournament_id_1)
        self.norcal_dao.delete_pending_tournament(pending_tournament)
        deleted_tournament = self.norcal_dao.get_pending_tournament_by_id(self.pending_tournament_id_1)
        self.assertIsNone(deleted_tournament)

    def test_update_tournament(self):
        tournament_1 = self.norcal_dao.get_tournament_by_id(self.tournament_id_1)
        self.assertEquals(tournament_1.id, self.tournament_id_1)
        self.assertEquals(tournament_1.type, self.tournament_type_1)
        self.assertEquals(tournament_1.raw, self.tournament_raw_1)
        self.assertEquals(tournament_1.date, self.tournament_date_1)
        self.assertEquals(tournament_1.name, self.tournament_name_1)
        self.assertEquals(tournament_1.matches, self.tournament_matches_1)
        self.assertEquals(tournament_1.players, self.tournament_players_1)
        self.assertEquals(tournament_1.regions, self.tournament_regions_1)

        tournament_2 = self.norcal_dao.get_tournament_by_id(self.tournament_id_2)
        self.assertEquals(tournament_2.id, self.tournament_id_2)
        self.assertEquals(tournament_2.type, self.tournament_type_2)
        self.assertEquals(tournament_2.raw, self.tournament_raw_2)
        self.assertEquals(tournament_2.date, self.tournament_date_2)
        self.assertEquals(tournament_2.name, self.tournament_name_2)
        self.assertEquals(tournament_2.matches, self.tournament_matches_2)
        self.assertEquals(tournament_2.players, self.tournament_players_2)
        self.assertEquals(tournament_2.regions, self.tournament_regions_2)

        tournament_2_raw_new = 'asdfasdf'
        tournament_2_name_new = 'new tournament 2 name'

        tournament_2.raw = tournament_2_raw_new
        tournament_2.name = tournament_2_name_new

        self.norcal_dao.update_tournament(tournament_2)

        tournament_1 = self.norcal_dao.get_tournament_by_id(self.tournament_id_1)
        self.assertEquals(tournament_1.id, self.tournament_id_1)
        self.assertEquals(tournament_1.type, self.tournament_type_1)
        self.assertEquals(tournament_1.raw, self.tournament_raw_1)
        self.assertEquals(tournament_1.date, self.tournament_date_1)
        self.assertEquals(tournament_1.name, self.tournament_name_1)
        self.assertEquals(tournament_1.matches, self.tournament_matches_1)
        self.assertEquals(tournament_1.players, self.tournament_players_1)
        self.assertEquals(tournament_1.regions, self.tournament_regions_1)

        tournament_2 = self.norcal_dao.get_tournament_by_id(self.tournament_id_2)
        self.assertEquals(tournament_2.id, self.tournament_id_2)
        self.assertEquals(tournament_2.type, self.tournament_type_2)
        self.assertEquals(tournament_2.raw, tournament_2_raw_new)
        self.assertEquals(tournament_2.date, self.tournament_date_2)
        self.assertEquals(tournament_2.name, tournament_2_name_new)
        self.assertEquals(tournament_2.matches, self.tournament_matches_2)
        self.assertEquals(tournament_2.players, self.tournament_players_2)
        self.assertEquals(tournament_2.regions, self.tournament_regions_2)

    def test_update_tournament_empty_raw(self):
        tournament_2 = self.norcal_dao.get_tournament_by_id(self.tournament_id_2)
        tournament_2.raw = ''

        with self.assertRaises(UpdateTournamentException):
            self.norcal_dao.update_tournament(tournament_2)


    def test_delete_tournament(self):
        tournament = self.norcal_dao.get_tournament_by_id(self.tournament_id_1)
        self.norcal_dao.delete_tournament(tournament)
        deleted_tournament = self.norcal_dao.get_tournament_by_id(self.tournament_id_1)
        self.assertIsNone(deleted_tournament)

    def test_get_all_tournament_ids(self):
        tournament_ids = self.norcal_dao.get_all_tournament_ids()

        self.assertEquals(len(tournament_ids), 2)
        self.assertEquals(tournament_ids[0], self.tournament_id_2)
        self.assertEquals(tournament_ids[1], self.tournament_id_1)

    def test_get_all_tournaments(self):
        tournaments = self.norcal_dao.get_all_tournaments()

        self.assertEquals(len(tournaments), 2)

        # tournament 1 is last in the list because it occurs later than tournament 2
        tournament_1 = tournaments[1]
        self.assertEquals(tournament_1.id, self.tournament_id_1)
        self.assertEquals(tournament_1.type, self.tournament_type_1)
        self.assertEquals(tournament_1.raw, '')
        self.assertEquals(tournament_1.date, self.tournament_date_1)
        self.assertEquals(tournament_1.name, self.tournament_name_1)
        self.assertEquals(tournament_1.matches, self.tournament_matches_1)
        self.assertEquals(tournament_1.players, self.tournament_players_1)
        self.assertEquals(tournament_1.regions, self.tournament_regions_1)

        tournament_2 = tournaments[0]
        self.assertEquals(tournament_2.id, self.tournament_id_2)
        self.assertEquals(tournament_2.type, self.tournament_type_2)
        self.assertEquals(tournament_2.raw, '')
        self.assertEquals(tournament_2.date, self.tournament_date_2)
        self.assertEquals(tournament_2.name, self.tournament_name_2)
        self.assertEquals(tournament_2.matches, self.tournament_matches_2)
        self.assertEquals(tournament_2.players, self.tournament_players_2)
        self.assertEquals(tournament_2.regions, self.tournament_regions_2)

    def test_get_all_tournaments_for_region(self):
        tournaments = self.norcal_dao.get_all_tournaments(regions=['norcal'])

        self.assertEquals(len(tournaments), 2)

        # tournament 1 is last in the list because it occurs later than tournament 2
        tournament_1 = tournaments[1]
        self.assertEquals(tournament_1.id, self.tournament_id_1)
        self.assertEquals(tournament_1.type, self.tournament_type_1)
        self.assertEquals(tournament_1.raw, '')
        self.assertEquals(tournament_1.date, self.tournament_date_1)
        self.assertEquals(tournament_1.name, self.tournament_name_1)
        self.assertEquals(tournament_1.matches, self.tournament_matches_1)
        self.assertEquals(tournament_1.players, self.tournament_players_1)
        self.assertEquals(tournament_1.regions, self.tournament_regions_1)

        tournament_2 = tournaments[0]
        self.assertEquals(tournament_2.id, self.tournament_id_2)
        self.assertEquals(tournament_2.type, self.tournament_type_2)
        self.assertEquals(tournament_2.raw, '')
        self.assertEquals(tournament_2.date, self.tournament_date_2)
        self.assertEquals(tournament_2.name, self.tournament_name_2)
        self.assertEquals(tournament_2.matches, self.tournament_matches_2)
        self.assertEquals(tournament_2.players, self.tournament_players_2)
        self.assertEquals(tournament_2.regions, self.tournament_regions_2)

        tournaments = self.norcal_dao.get_all_tournaments(regions=['texas'])

        self.assertEquals(len(tournaments), 1)

        tournament_2 = tournaments[0]
        self.assertEquals(tournament_2.id, self.tournament_id_2)
        self.assertEquals(tournament_2.type, self.tournament_type_2)
        self.assertEquals(tournament_2.raw, '')
        self.assertEquals(tournament_2.date, self.tournament_date_2)
        self.assertEquals(tournament_2.name, self.tournament_name_2)
        self.assertEquals(tournament_2.matches, self.tournament_matches_2)
        self.assertEquals(tournament_2.players, self.tournament_players_2)
        self.assertEquals(tournament_2.regions, self.tournament_regions_2)

    def test_get_all_tournaments_containing_players(self):
        players = [self.player_5]

        tournaments = self.norcal_dao.get_all_tournaments(players=players)
        self.assertEquals(len(tournaments), 1)

        tournament = tournaments[0]
        self.assertEquals(tournament.id, self.tournament_id_2)
        self.assertEquals(tournament.type, self.tournament_type_2)
        self.assertEquals(tournament.raw, '')
        self.assertEquals(tournament.date, self.tournament_date_2)
        self.assertEquals(tournament.name, self.tournament_name_2)
        self.assertEquals(tournament.matches, self.tournament_matches_2)
        self.assertEquals(tournament.players, self.tournament_players_2)
        self.assertEquals(tournament.regions, self.tournament_regions_2)

    def test_get_all_tournaments_containing_players_and_regions(self):
        players = [self.player_2]
        regions = ['texas']

        tournaments = self.norcal_dao.get_all_tournaments(players=players, regions=regions)
        self.assertEquals(len(tournaments), 1)

        tournament = tournaments[0]
        self.assertEquals(tournament.id, self.tournament_id_2)
        self.assertEquals(tournament.type, self.tournament_type_2)
        self.assertEquals(tournament.raw, '')
        self.assertEquals(tournament.date, self.tournament_date_2)
        self.assertEquals(tournament.name, self.tournament_name_2)
        self.assertEquals(tournament.matches, self.tournament_matches_2)
        self.assertEquals(tournament.players, self.tournament_players_2)
        self.assertEquals(tournament.regions, self.tournament_regions_2)

    def test_get_tournament_by_id(self):
        tournament_1 = self.norcal_dao.get_tournament_by_id(self.tournament_id_1)
        self.assertEquals(tournament_1.id, self.tournament_id_1)
        self.assertEquals(tournament_1.type, self.tournament_type_1)
        self.assertEquals(tournament_1.raw, self.tournament_raw_1)
        self.assertEquals(tournament_1.date, self.tournament_date_1)
        self.assertEquals(tournament_1.name, self.tournament_name_1)
        self.assertEquals(tournament_1.matches, self.tournament_matches_1)
        self.assertEquals(tournament_1.players, self.tournament_players_1)
        self.assertEquals(tournament_1.regions, self.tournament_regions_1)

        tournament_2 = self.norcal_dao.get_tournament_by_id(self.tournament_id_2)
        self.assertEquals(tournament_2.id, self.tournament_id_2)
        self.assertEquals(tournament_2.type, self.tournament_type_2)
        self.assertEquals(tournament_2.raw, self.tournament_raw_2)
        self.assertEquals(tournament_2.date, self.tournament_date_2)
        self.assertEquals(tournament_2.name, self.tournament_name_2)
        self.assertEquals(tournament_2.matches, self.tournament_matches_2)
        self.assertEquals(tournament_2.players, self.tournament_players_2)
        self.assertEquals(tournament_2.regions, self.tournament_regions_2)

        self.assertIsNone(self.norcal_dao.get_tournament_by_id(ObjectId()))

    def test_get_players_with_similar_alias(self):
        self.assertEquals(self.norcal_dao.get_players_with_similar_alias('gar'), [self.player_1, self.player_3])
        self.assertEquals(self.norcal_dao.get_players_with_similar_alias('GAR'), [self.player_1, self.player_3])
        self.assertEquals(self.norcal_dao.get_players_with_similar_alias('g a r'), [self.player_1, self.player_3])
        self.assertEquals(self.norcal_dao.get_players_with_similar_alias('garpr | gar'), [self.player_1, self.player_3])

    def test_merge_players(self):
        self.norcal_dao.merge_players(source=self.player_5, target=self.player_1)

        tournament_1 = self.norcal_dao.get_tournament_by_id(self.tournament_id_1)
        self.assertEquals(tournament_1.id, self.tournament_id_1)
        self.assertEquals(tournament_1.type, self.tournament_type_1)
        self.assertEquals(tournament_1.raw, self.tournament_raw_1)
        self.assertEquals(tournament_1.date, self.tournament_date_1)
        self.assertEquals(tournament_1.name, self.tournament_name_1)
        self.assertEquals(tournament_1.matches, self.tournament_matches_1)
        self.assertEquals(tournament_1.players, self.tournament_players_1)
        self.assertEquals(tournament_1.regions, self.tournament_regions_1)

        tournament_2 = self.norcal_dao.get_tournament_by_id(self.tournament_id_2)
        self.assertEquals(tournament_2.id, self.tournament_id_2)
        self.assertEquals(tournament_2.type, self.tournament_type_2)
        self.assertEquals(tournament_2.raw, self.tournament_raw_2)
        self.assertEquals(tournament_2.date, self.tournament_date_2)
        self.assertEquals(tournament_2.name, self.tournament_name_2)
        self.assertEquals(set(tournament_2.players), set(self.tournament_players_1))
        self.assertEquals(len(tournament_2.matches), len(self.tournament_matches_1))
        self.assertEquals(tournament_2.matches[0], self.tournament_matches_1[0])
        self.assertEquals(tournament_2.matches[1], self.tournament_matches_1[1])
        self.assertEquals(tournament_2.regions, self.tournament_regions_2)

        merged_player_aliases = set(['gar', 'garr', 'pewpewu'])
        merged_player_regions = set(['norcal', 'texas', 'socal'])
        merged_player = self.norcal_dao.get_player_by_id(self.player_1_id)
        self.assertEquals(merged_player.id, self.player_1_id)
        self.assertEquals(merged_player.name, self.player_1.name)
        self.assertEquals(set(merged_player.aliases), merged_player_aliases)
        self.assertEquals(set(merged_player.regions), merged_player_regions)

        self.assertIsNone(self.norcal_dao.get_player_by_id(self.player_5_id))

    def test_merge_players_none(self):
        with self.assertRaises(TypeError):
            self.norcal_dao.merge_players()

        with self.assertRaises(TypeError):
            self.norcal_dao.merge_players(source=self.player_1)

        with self.assertRaises(TypeError):
            self.norcal_dao.merge_players(target=self.player_1)

    def test_merge_players_same_player(self):
        with self.assertRaises(ValueError):
            self.norcal_dao.merge_players(source=self.player_1, target=self.player_1)

    # TODO
    def test_merge_players_same_player_in_single_match(self):
        pass

    def test_get_latest_ranking(self):
        latest_ranking = self.norcal_dao.get_latest_ranking()

        self.assertEquals(latest_ranking.time, self.ranking_time_2)
        self.assertEquals(latest_ranking.tournaments, self.tournament_ids)

        rankings = latest_ranking.ranking

        self.assertEquals(len(rankings), 3)
        self.assertEquals(rankings[0], self.ranking_entry_1)
        self.assertEquals(rankings[1], self.ranking_entry_2)
        self.assertEquals(rankings[2], self.ranking_entry_4)


    def test_get_all_users(self):
        users = self.norcal_dao.get_all_users()
        self.assertEquals(len(users), 2)

        user = users[0]
        self.assertEquals(user.id, self.user_id_1)
        self.assertEquals(user.username, 'user1')
        self.assertEquals(user.admin_regions, self.user_admin_regions_1)

        user = users[1]
        self.assertEquals(user.id, self.user_id_2)
        self.assertEquals(user.username, self.user_full_name_2)
        self.assertEquals(user.admin_regions, self.user_admin_regions_2)

    def test_create_user(self):
        username = 'abra'
        password = 'cadabra'
        regions = ['nyc', 'newjersey']

        self.norcal_dao.create_user(username, password, regions)

        users = self.norcal_dao.get_all_users()
        self.assertEquals(len(users), 3)

        user = users[-1]
        self.assertEquals(user.username, username)
        self.assertEquals(user.admin_regions, regions)

    def test_create_duplicate_user(self):
        username = 'abra'
        password = 'cadabra'
        regions = ['nyc', 'newjersey']

        self.norcal_dao.create_user(username, password, regions)
        with self.assertRaises(DuplicateUsernameException):
            self.norcal_dao.create_user(username, password, regions)

    def test_create_user_invalid_regions(self):
        username = 'abra'
        password = 'cadabra'
        regions = ['canadia', 'bahstahn']

        with self.assertRaises(InvalidRegionsException):
            self.norcal_dao.create_user(username, password, regions)

    def test_change_password(self):
        username = 'abra'
        password = 'cadabra'
        new_password = 'whoops'
        regions = ['newjersey']

        self.norcal_dao.create_user(username, password, regions)
        user = self.norcal_dao.get_user_by_id_or_none(username)
        old_salt = user.salt
        old_hash = user.hashed_password
        self.assertTrue(verify_password(password, old_salt, old_hash))

        self.norcal_dao.change_passwd(username, new_password)
        new_user = self.norcal_dao.get_user_by_id_or_none(username)
        new_salt = new_user.salt
        new_hash = new_user.hashed_password

        self.assertNotEquals(old_salt, new_salt)
        self.assertTrue(verify_password(new_password, new_salt, new_hash))


    def test_get_and_insert_pending_merge(self):
        dao = self.norcal_dao
        all_players = dao.get_all_players()
        player_one = all_players[0]
        player_two = all_players[1]
        users = dao.get_all_users()
        user = users[0]
        now = datetime.today()
        orig_id = ObjectId()
        the_merge = Merge(user.id, player_one.id, player_two.id, now, id=orig_id)

        merge_id = dao.insert_pending_merge(the_merge)

        self.assertTrue(merge_id)
        self.assertIsInstance(merge_id, ObjectId)
        self.assertEqual(merge_id, orig_id)

        the_merge_redux = dao.get_pending_merge(merge_id)

        self.assertEqual(the_merge.base_player_obj_id, the_merge_redux.base_player_obj_id, msg=the_merge_redux)
        self.assertEqual(the_merge.player_to_be_merged_obj_id, the_merge_redux.player_to_be_merged_obj_id)
        self.assertEqual(the_merge.id, the_merge_redux.id)
        self.assertEqual(the_merge.requester_user_id, the_merge_redux.requester_user_id)
        # changed to account for mongo driver losing sub-second accuracy on datetimes
        self.assertTrue(abs(the_merge.time - the_merge_redux.time).total_seconds() < 1)

    def test_get_non_existant_merge(self):
        dao = self.norcal_dao
        self.assertIsNone(dao.get_pending_merge(ObjectId("420f53650181b84aaaa01051"))) #mlg1337noscope

    def test_get_players_with_similar_alias(self):
        dao = self.norcal_dao
        self.assertTrue(any(player.name == "gaR" for player in dao.get_players_with_similar_alias("1 1 gar")))
        self.assertTrue(any(player.name == "gaR" for player in dao.get_players_with_similar_alias("p1s1 gar")))
        self.assertTrue(any(player.name == "gaR" for player in dao.get_players_with_similar_alias("GOOG| gar")))
        self.assertTrue(any(player.name == "gaR" for player in dao.get_players_with_similar_alias("GOOG | gar")))
        self.assertTrue(any(player.name == "gaR" for player in dao.get_players_with_similar_alias("p1s2 GOOG| gar")))
        self.assertTrue(any(player.name == "gaR" for player in dao.get_players_with_similar_alias("garpr goog youtube gar")))
