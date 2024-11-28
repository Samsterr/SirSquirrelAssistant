from src import common, mirror_utils
from src.core import skill_check,reconnect, battle, check_loading, transition_loading,post_run_load, battle_check
import logging
    
class Mirror:
    def __init__(self, status):
        self.status = status
        self.logger = logging.getLogger(__name__)
        self.squad_order = self.set_sinner_order(status)
        self.aspect_ratio = common.get_aspect_ratio()
        self.res_x, self.res_y = common.get_resolution()
        self.squad_set = False

    @staticmethod
    def floor_id():
        """Returns what floor is currently on"""
        floor = ""
        if common.element_exist('pictures/mirror/packs/floor1.png',0.95):
            floor = "f1"
        if common.element_exist('pictures/mirror/packs/floor2.png',0.95):
            floor = "f2"
        if common.element_exist('pictures/mirror/packs/floor3.png',0.95):
            floor = "f3"
        if common.element_exist('pictures/mirror/packs/floor4.png',0.95):
            floor = "f4"
        if common.element_exist('pictures/mirror/packs/floor5.png',0.95):
            floor = "f5"
        return floor
        
    @staticmethod
    def set_sinner_order(status):
        """Gets the squad order for the team status"""
        if mirror_utils.squad_choice(status) is None:
            return common.squad_order("default")
        else:
            return common.squad_order(status)

    def setup_mirror(self):
        """Main Mirror Logic of identifying and running the specified function"""
        common.click_matching("pictures/mirror/general/md_enter.png")

        if common.element_exist("pictures/mirror/general/explore_reward.png"): #needs to test
            self.logger.info("Existing Run Detected")
            if common.element_exist("pictures/mirror/general/clear.png"):
                self.logger.info("Run Cleared")
                common.click_matching("pictures/general/md_claim.png")
                if common.element_exist("pictures/general/confirm_w.png"):
                    self.logger.info("Rewards Claimed")
                    common.click_matching("pictures/general/confirm_w.png")
                    common.click_matching("pictures/general/confirm_b.png")
                    common.click_matching("pictures/general/cancel.png")
            else:
                self.logger.info("Run Not Cleared, Giving Up")
                common.click_matching("pictures/general/give_up.png")
                common.click_matching("pictures/general/cancel.png")

        if common.element_exist("pictures/general/resume.png"): #check if md is in progress
            common.click_matching("pictures/general/resume.png")
            check_loading()
            self.logger.info("Resuming Run")

        if common.element_exist("pictures/general/enter.png"): #Fresh run
            common.click_matching("pictures/general/enter.png")
            common.sleep(1) #Transitional 
            self.logger.info("Starting Run")

        if common.element_exist("pictures/mirror/general/squad_select.png"): #checks if in Squad select
            self.initial_squad_selection()

        if common.element_exist("pictures/mirror/grace/grace_menu.png"):
            self.grace_of_stars()

        if common.element_exist("pictures/mirror/general/gift_select.png"): #Checks if in gift select
            self.gift_selection()
    
    def check_run(self):
        run_complete = 0
        win_flag = 0
        if common.element_exist("pictures/general/defeat.png"):
            self.defeat()
            run_complete = 1
            win_flag = 0

        if common.element_exist("pictures/general/victory.png"):
            self.victory()
            run_complete = 1
            win_flag = 1

        return win_flag,run_complete

    def mirror_loop(self):
        if common.element_exist("pictures/mirror/general/danteh.png"): #checks if currently navigating
            self.navigation()

        if common.element_exist("pictures/events/skip.png"): #if hitting the events click skip to determine which is it
            self.logger.info("Entered ? node")
            common.mouse_move(200,200)
            common.click_skip(4)

        if common.element_exist("pictures/mirror/general/event.png"):
            self.event_choice()

        if common.element_exist("pictures/mirror/restshop/shop.png"):
            self.rest_shop()

        if common.element_exist("pictures/battle/clear.png"): #checks if in squad select and then proceeds with battle
            self.squad_select()

        if common.element_exist("pictures/battle/winrate.png"):
            battle()

        if common.element_exist("pictures/mirror/general/reward_select.png"): #checks if in reward select
            self.reward_select()

        if common.element_exist("pictures/mirror/general/encounter_reward.png"): #checks if in encounter rewards
            self.encounter_reward_select()            

        if common.element_exist("pictures/mirror/general/inpack.png"): #checks if in pack select
            self.pack_selection()

        if common.element_exist("pictures/general/server_error.png"):
            reconnect()

        if common.element_exist("pictures/mirror/general/ego_gift_get.png"): #handles the ego gift get
            self.logger.info("Handling EGO GIFT Prompt")
            common.click_matching("pictures/general/confirm_b.png")

        if common.element_exist("pictures/general/maint.png"):
            common.click_matching("pictures/general/close.png")
            common.sleep(0.5)
            common.click_matching("pictures/general/no_op.png")
            common.click_matching("pictures/general/close.png")
            self.logger.info("SERVER UNDERGOING MAINTAINANCE, BOT WILL STOP NOW!")
            exit()

        return self.check_run()

    def grace_of_stars(self):
        self.logger.info("Selecting Grace")
        found = common.match_image("pictures/mirror/grace/grace.png")
        grace = len(found) # The number of stars translate to about 60 post update but at least 30 right now
        grace_blessing = mirror_utils.grace_choice(grace)
        self.logger.info("Blessing amount at least: " + str(grace) + "0")
        common.click_matching(grace_blessing,0.95)
        common.click_matching("pictures/mirror/general/enter_b.png")
        common.click_matching("pictures/general/confirm_b.png")
        return
    
    def gift_selection(self):
        """selects the ego gift of the same status, fallsback on random if not unlocked"""
        self.logger.info("E.G.O Gift Selection")
        #initial_gift_coords = [420,580,740] #The side bar location for EGO Gifts

        gift = mirror_utils.gift_choice(self.status) or "pictures/mirror/gifts/random.png"
        if common.element_exist(gift,0.9) is None: #Search for gift and if not present scroll to find it
            found = common.match_image("pictures/mirror/general/gift_select.png")
            x,y = found[0]
            common.mouse_move(x - common.scale_x(1365),y + common.scale_y(50))
            for i in range(5):
                common.mouse_scroll(-1000)
        
        if common.element_exist(gift,0.9) is None: # i forgot to check again if it is not found
            gift = "pictures/mirror/gifts/random.png"
            #self.status = "random" #Reset the gift to fail the squad selection check
            #self.squad_order = self.set_sinner_order("default") #Uses the default squad

        found = common.match_image("pictures/mirror/general/gift_select.png")
        x,y = found[0]
        y = y + common.uniform_scale_single(235)
        initial_gift_coords = [y, y+common.uniform_scale_single(190), y+common.uniform_scale_single(190*2)]
        #if self.status == "sinking" or self.status == "slash": #Other 2 gifts better
        #       initial_gift_coords.pop(0)
        #else:
        #       initial_gift_coords.pop(2)

        common.click_matching(gift,0.9) #click on specified
        for i in initial_gift_coords:
            common.mouse_move_click(common.uniform_scale_single(1640),i)
        #common.mouse_move_click(common.uniform_scale_single(1640),initial_gift_coords[1])
        common.click_matching("pictures/mirror/general/confirm_gift.png")
        for i in range(3):
            if common.element_exist("pictures/mirror/general/ego_gift_get.png"): #handles the ego gift get
                common.click_matching("pictures/general/confirm_b.png")
         
                #common.sleep(0.5)
        #common.sleep(0.5)
        check_loading()

    def initial_squad_selection(self):
        """Searches for the squad name with the status type, if not found then uses the current squad"""
        self.logger.info("Mirror Dungeon Squad Select")
        status = mirror_utils.squad_choice(self.status)
        if status is None:
            common.key_press("enter")
            self.status = "poise"
            return
        #This is to bring us to the first entry of teams
        found = common.match_image("pictures/mirror/general/squad_select.png")
        x,y = found[0]
        common.mouse_move(x+common.uniform_scale_single(90),y+common.uniform_scale_single(90))
        for i in range(30):
            common.mouse_scroll(1000)
        #scrolls through all the squads in steps to look for the name
        for _ in range(4):
            if common.element_exist(status) is None:
                for i in range(7):
                    common.mouse_scroll(-1000)
                common.sleep(1)
                if common.element_exist(status):
                    common.click_matching(status)
                    break
                continue
            else:
                common.click_matching(status)
                break
        common.key_press("enter")
        common.sleep(1) #Transitional to Grace of Dreams
        #check_loading() #Theres a load screen when going from Squad to Pack

    def pack_selection(self):
        """Prioritises the status gifts for packs if not follows a list"""
        self.logger.info("Selecting Pack")
        status = mirror_utils.pack_choice(self.status) or "pictures/mirror/packs/status/poise_pack.png"
        floor = self.floor_id()
        self.logger.debug("Current Floor "+ floor)
        if floor == "f1":
            common.sleep(3) # the ego gift crediting blocks the refresh button
        found = common.match_image("pictures/mirror/general/refresh.png")
        x,y = found[0]
        self.logger.debug(common.luminence(x,y))
        refresh_flag = common.luminence(x,y) < 70 #Test
        common.mouse_move(200,200)
        common.sleep(2)
        #TESTING 0.8 on Statuses
        if self.exclusion_detection(floor) and not refresh_flag: #if pack exclusion detected and not refreshed
            self.logger.debug("PACKS: pack exclusion detected, refreshing")
            common.click_matching("pictures/mirror/general/refresh.png")
            common.mouse_move(200,200)
            return self.pack_selection()

        if self.exclusion_detection(floor) and refresh_flag: #if pack exclusion detected and refreshed
            self.logger.debug("PACKS: pack exclusion detected and refreshed, choosing from pack")
            return self.pack_list(floor)

        if common.element_exist(status) and not self.exclusion_detection(floor) and floor != "f4": #if pack exclusion absent and status exists
            self.logger.debug("pack exclusion not detected, status detceted, choosing from status")
            return self.choose_pack(status)

        if common.element_exist(status) and self.exclusion_detection(floor) and not refresh_flag: #if pack detected and status detected and not refreshed
            self.logger.debug("PACKS: pack exclusion detected, status detected, refreshing")
            common.click_matching("pictures/mirror/general/refresh.png")
            return self.pack_selection()

        self.logger.debug("PACKS: using pack list")
        return self.pack_list(floor)

    def pack_list(self,floor, threshold=0.8):
        with open("config/" + floor + ".txt", "r") as f:
            packs = [i.strip() for i in f.readlines()] #uses the f1,f2,f3,f4 txts for floor order
        for i in packs:
            if common.element_exist(i,threshold):
                return self.choose_pack(i, threshold)

    def choose_pack(self,pack_image, threshold=0.8):
        found = common.match_image(pack_image,threshold)
        x,y = common.random_choice(found)
        common.mouse_move(x,y-common.uniform_scale_single(350))
        common.mouse_drag(x,y)
        transition_loading()
        return

    def exclusion_detection(self,floor):
        """Detects an excluded pack"""
        detected = 0
        if floor == "f1":
            return detected
        if floor == "f2":
            return detected
        if floor == "f3":    
            exclusion = ["pictures/mirror/packs/f3/flood.png"]
        if floor == "f4":
            exclusion = ["pictures/mirror/packs/f4/wrath.png",
                       "pictures/mirror/packs/f4/pride.png",
                       "pictures/mirror/packs/f4/yield.png",
                       "pictures/mirror/packs/f4/sloth.png",
                       "pictures/mirror/packs/f4/crawling.png",
                       "pictures/mirror/packs/f4/violet.png"]
        if floor == "f5":
            exclusion = ["pictures/mirror/packs/f5/crawling.png",
                         "pictures/mirror/packs/f5/yield.png",
                         "pictures/mirror/packs/f5/slicers.png",
                         "pictures/mirror/packs/f5/sloth.png"]
            
        detected = any(common.element_exist(i) for i in exclusion) #use 0.75 if current has issues
        return int(detected)

    def squad_select(self):
        """selects sinners in squad order"""
        self.logger.info("Selecting Squad for Battle")
        if not self.squad_set or not common.element_exist("pictures/squads/full_squad.png"):
            common.click_matching("pictures/battle/clear.png")
            if common.element_exist("pictures/general/confirm_w.png"):
                common.click_matching("pictures/general/confirm_w.png")
            for i in self.squad_order: #click squad members according to the order in the json file
                x,y = i
                common.mouse_move_click(x,y)
            self.squad_set = True
        common.click_matching("pictures/squads/squad_select.png")
        #common.key_press("enter")
        check_loading()

    def reward_select(self):
        """Selecting EGO Gift rewards"""
        self.logger.info("Reward Selection")
        status_effect = mirror_utils.reward_choice(self.status)
        if status_effect is None:
            status_effect = "pictures/mirror/rewards/poise_reward.png"
        if common.element_exist(status_effect) is None:
            found = common.match_image("pictures/mirror/general/reward_select.png")
            x,y = common.random_choice(found)
            common.mouse_move_click(x,y)
        else:
            found = common.match_image(status_effect)
            x,y = common.random_choice(found)
            common.mouse_move_click(x,y)

        common.click_matching("pictures/mirror/general/confirm_gift.png")
        common.sleep(1)
        common.click_matching("pictures/general/confirm_b.png")
        #common.key_press("enter")

    def encounter_reward_select(self):
        """Select Encounter Rewards prioritising starlight first"""
        self.logger.info("Encounter Reward Selection")
        encounter_reward = ["pictures/mirror/encounter_reward/cost_gift.png",
                            "pictures/mirror/encounter_reward/cost.png",
                            "pictures/mirror/encounter_reward/gift.png",
                            "pictures/mirror/encounter_reward/resource.png"]
        common.sleep(0.5)
        for rewards in encounter_reward:
            if common.element_exist(rewards):
                common.click_matching(rewards)
                common.click_matching("pictures/general/confirm_b.png")
                common.sleep(1)
                if common.element_exist("pictures/mirror/encounter_reward/prompt.png"):
                    common.key_press("enter")
                    break
                if common.element_exist("pictures/mirror/general/ego_gift_get.png"): #handles the ego gift get
                    common.click_matching("pictures/general/confirm_b.png")
                break
        common.sleep(3) #needs to wait for the gain to credits

    #needs work
    def navigation(self):
        """Core navigation function to reach the end of floor"""
        self.logger.info("Navigating")
        node_y = [607,189,1036,820,396]
        #Checks incase continuing quitted out MD
        common.click_matching("pictures/mirror/general/danteh.png")
        if common.element_exist("pictures/mirror/general/nav_enter.png"):
            common.click_matching("pictures/mirror/general/nav_enter.png")
            #common.key_press("enter")
        else:
        #Find which node is the traversable one
            for i in node_y:
                if self.aspect_ratio == "4:3":
                    common.mouse_move_click(common.uniform_scale_single(1444),common.uniform_scale_single(i) + common.uniform_scale_coordinates(105))
                else:
                    common.mouse_move_click(common.uniform_scale_single(1444),common.uniform_scale_single(i))
                common.sleep(1)
                if common.element_exist("pictures/mirror/general/nav_enter.png"):
                    common.click_matching("pictures/mirror/general/nav_enter.png")
                    #common.key_press("enter")
                    break

    def sell_gifts(self):
        for _ in range(3):
            common.sleep(1)
            if common.element_exist("pictures/mirror/restshop/market/vestige_2.png"):
                common.click_matching("pictures/mirror/restshop/market/vestige_2.png")
                common.click_matching("pictures/mirror/restshop/market/sell_b.png")
                common.click_matching("pictures/general/confirm_w.png")
                self.logger.debug("SOLD VESTIGE")

            if common.element_exist("pictures/mirror/restshop/market/vestige_1.png"):
                common.click_matching("pictures/mirror/restshop/market/vestige_1.png")
                common.click_matching("pictures/mirror/restshop/market/sell_b.png")
                common.click_matching("pictures/general/confirm_w.png")
                self.logger.debug("SOLD VESTIGE")

            if common.element_exist("pictures/mirror/restshop/scroll_bar.png"):
                common.click_matching("pictures/mirror/restshop/scroll_bar.png")
                for k in range(5):
                    common.mouse_scroll(-1000)

    def rest_shop(self):
        #Flow should be Sell > Heal > Enhance > Buy since cost is scarce and stronger gifts is better
        self.logger.info("REST SHOP")
        #SELLING
        common.click_matching("pictures/mirror/restshop/market/sell_gifts.png")
        if common.element_exist("pictures/mirror/restshop/scroll_bar.png"): #if scroll bar present scrolls to the start
            common.click_matching("pictures/mirror/restshop/scroll_bar.png")
            for i in range(5):
                common.mouse_scroll(1000)
        self.logger.debug("CHECKING FOR SELLABLE GIFTS")
        self.sell_gifts()
        common.click_matching("pictures/mirror/restshop/close.png")

        #Check for insufficient cost to exit
        if common.element_exist("pictures/mirror/restshop/small_not.png"):
            self.logger.debug("REST SHOP: NOT ENOUGH COST, EXITING RESTSHOP")
            common.click_matching("pictures/mirror/restshop/leave.png")
            common.click_matching("pictures/general/confirm_w.png") 
            
        else:
            #HEALING
            common.click_matching("pictures/mirror/restshop/heal.png")
            common.click_matching("pictures/mirror/restshop/heal_all.png")
            self.logger.info("REST SHOP: HEALED ALL SINNERS")
            common.sleep(0.5)
            common.click_matching("pictures/mirror/restshop/return.png")

            #ENHANCING
            status = mirror_utils.enhance_gift_choice(self.status)
            if status is None:
                status = "pictures/mirror/restshop/enhance/poise_enhance.png"
            common.click_matching("pictures/mirror/restshop/enhance/enhance.png")
            self.logger.debug("REST SHOP: ENHANCING EGO GIFTS")
            if common.element_exist("pictures/mirror/restshop/scroll_bar.png"): #if scroll bar present scrolls to the start
                common.click_matching("pictures/mirror/restshop/scroll_bar.png")
                for i in range(5):
                    common.mouse_scroll(1000)
            self.enhance_gifts(status)
            if common.element_exist("pictures/mirror/restshop/close.png"):
                common.click_matching("pictures/mirror/restshop/close.png")
                #common.click_matching("pictures/mirror/reststop/leave.png")
                #common.click_matching("pictures/general/confirm_w.png")

            #BUYING
            status = mirror_utils.market_choice(self.status)
            if status is None:
                status = "pictures/mirror/market/poise_market.png"
            for _ in range(3):
                market_gifts = []
                if common.element_exist(status):
                    market_gifts += common.match_image(status)
                #keywordless gifts
                if common.element_exist("pictures/mirror/restshop/market/wordless.png"):
                    market_gifts += common.match_image("pictures/mirror/restshop/market/wordless.png")
                if len(market_gifts):
                    for i in market_gifts:
                        x,y = i
                        self.logger.debug(common.luminence(x+common.scale_x(31),y+common.scale_y(1)))
                        if common.luminence(x+common.scale_x(31),y+common.scale_y(1)) < 6: #this area will have a value of less than or equal to 5 if purchased
                            continue
                        if common.element_exist("pictures/mirror/restshop/small_not.png"):
                            self.logger.debug("REST SHOP: NOT ENOUGH COST AFTER PURCHASE, EXITING MARKET")
                            break
                        common.mouse_move_click(x,y)
                        if common.element_exist("pictures/mirror/restshop/market/purchase.png"): #purchase button will appear if purchasable
                            self.logger.debug("MARKET: PURCHASED EGO GIFT")
                            common.click_matching("pictures/mirror/restshop/market/purchase.png")
                            common.click_matching("pictures/general/confirm_b.png")

                if common.element_exist("pictures/mirror/restshop/small_not.png"):
                    break

                if _ != 2:
                    common.click_matching("pictures/mirror/restshop/market/refresh.png")


        #LEAVING
        common.click_matching("pictures/mirror/restshop/leave.png")
        common.click_matching("pictures/general/confirm_w.png")
        return
    
    #def market_shopping(self):
    #    """Handles Market Node"""
    #    #If everyone not at 45 sanity then heal
    #    self.logger.info("Marketplace")
    #    refresh_flag = 0
    #    status = mirror_utils.market_choice(self.status)
    #    if status is None:
    #        status = "pictures/mirror/market/poise_market.png"
#
    #    #Check for insufficient cost to exit
    #    if common.element_exist("pictures/mirror/market/small_not.png"):
    #        self.logger.debug("MARKET: Not enough cost, exiting market")
    #        common.click_matching("pictures/mirror/market/leave.png")
    #        common.click_matching("pictures/general/confirm_w.png")
#
    #    else:
    #        common.click_matching("pictures/mirror/market/heal.png")
    #        if common.element_exist("pictures/mirror/market/heal_all.png"): #if you cant afford this will not show up so check for it
    #            found = common.match_image("pictures/mirror/market/heal_all.png")
    #            x,y = found[0]
    #            self.logger.debug(common.luminence(x,y))
    #            if common.luminence(x,y) > 8:
    #                self.logger.debug("MARKET: HEALING ALL")
    #                common.click_matching("pictures/mirror/market/heal_all.png")
    #                common.wait_skip("pictures/events/continue.png")
    #            else:
    #                self.logger.debug("MARKET: Sinners Maxxed HP/SP")
    #                common.click_matching("pictures/mirror/market/back.png")
#
    #        for _ in range(3):
    #            market_gifts = []
    #            if common.element_exist(status):
    #                market_gifts += common.match_image(status)
    #            #keywordless gifts
    #            if common.element_exist("pictures/mirror/market/wordless.png"):
    #                market_gifts += common.match_image("pictures/mirror/market/wordless.png")
    #            if len(market_gifts):
    #                for i in market_gifts:
    #                    x,y = i
    #                    self.logger.debug(common.luminence(x+common.scale_x(31),y+common.scale_y(1)))
    #                    if common.luminence(x+common.scale_x(31),y+common.scale_y(1)) < 6: #this area will have a value of less than or equal to 5 if purchased
    #                        continue
    #                    if common.element_exist("pictures/mirror/market/small_not.png"):
    #                        self.logger.debug("MARKET: NOT ENOUGH COST AFTER PURCHASE, EXITING MARKET")
    #                        break
    #                    common.mouse_move_click(x,y)
    #                    if common.element_exist("pictures/mirror/market/purchase.png"): #purchase button will appear if purchasable
    #                        self.logger.debug("MARKET: PURCHASED EGO GIFT")
    #                        common.click_matching("pictures/mirror/market/purchase.png")
    #                        common.click_matching("pictures/general/confirm_b.png")
#
    #            if common.element_exist("pictures/mirror/market/small_not.png"):
    #                break
#
    #            if _ != 2:
    #                common.click_matching("pictures/mirror/market/refresh.png")
#
    #        common.click_matching("pictures/mirror/market/leave.png")
    #        common.click_matching("pictures/general/confirm_w.png")    

    #def rest_stop(self):
    #    #check for insufficient cost
    #    self.logger.info("Rest Stop")
    #    if common.element_exist("pictures/mirror/reststop/no_cost.png"):
    #        self.logger.debug("REST STOP: NOT ENOUGH COST, EXITING REST STOP")
    #        common.click_matching("pictures/mirror/reststop/no_cost.png")
    #        common.click_matching("pictures/mirror/reststop/leave.png")
    #        common.click_matching("pictures/general/confirm_w.png")
#
    #    else:
    #        status = mirror_utils.enhance_gift_choice(self.status)
    #        if status is None:
    #            status = "pictures/mirror/reststop/poise_enhance.png"
    #        #if not common.element_exist("pictures/mirror/reststop/sanity.png") or (common.element_exist("pictures/mirror/reststop/sanity.png")\
    #        #and len(common.match_image("pictures/mirror/reststop/sanity.png")) < 12): #Heal if all 12 sinners arent 45 Sanity
#
    #        common.click_matching("pictures/mirror/reststop/heal_sinner.png")
    #        if common.element_exist("pictures/mirror/reststop/heal_all.png"): #checks if prompt does enter
    #            found = common.match_image("pictures/mirror/reststop/heal_all.png")
    #            x,y = found[0]
    #            self.logger.debug(common.luminence(x,y))
    #            if common.luminence(x,y) < 7:
    #                self.logger.debug("REST STOP: UNSUCCESSFULLY HEALED SINNERS")
    #                common.click_matching("pictures/mirror/reststop/back.png")#unsuccessful heal 
    #            else:
    #                common.click_matching("pictures/mirror/reststop/heal_all.png") #This is to check for successful healing
    #                self.logger.debug("REST STOP: HEALING ALL SINNERS")
    #                common.wait_skip("pictures/events/continue.png")
#
    #        common.click_matching("pictures/mirror/reststop/enhance.png")
    #        self.logger.debug("REST STOP: ENHANCING EGO GIFTS")
    #        if common.element_exist("pictures/mirror/reststop/scroll_bar.png"): #if scroll bar present scrolls to the start
    #            common.click_matching("pictures/mirror/reststop/scroll_bar.png")
    #            for i in range(5):
    #                common.mouse_scroll(1000)
    #        self.enhance_gifts(status)
    #        if common.element_exist("pictures/mirror/reststop/close.png"):
    #            common.click_matching("pictures/mirror/reststop/close.png")
    #        common.click_matching("pictures/mirror/reststop/leave.png")
    #        common.click_matching("pictures/general/confirm_w.png")

    def upgrade(self,status,shift_x,shift_y):
        gifts = common.match_image(status)
        for x,y in gifts:
            self.logger.debug(common.luminence(x+common.uniform_scale_single(shift_x),y+common.uniform_scale_single(shift_y)))
            if common.luminence(x+common.uniform_scale_single(shift_x),y+common.uniform_scale_single(shift_y)) < 21: #19.66 is for upgraded and 14.33 is for greyed out so 20 should work for now
                continue
            common.mouse_move_click(x,y)
            for _ in range(2): #upgrading twice
                if common.element_exist("pictures/mirror/restshop/enhance/fully_upgraded.png"): #if fully upgraded skip this item
                    break
                common.click_matching("pictures/mirror/restshop/enhance/power_up.png")
                if common.element_exist("pictures/mirror/restshop/enhance/more.png"): #If player has no more cost exit
                    self.logger.debug("REST SHOP: NOT ENOUGH COST, EXITING ENHANCE PAGE")
                    common.click_matching("pictures/mirror/restshop/enhance/cancel.png")
                    common.sleep(1)
                    common.mouse_click()
                    return
                elif common.element_exist("pictures/mirror/restshop/enhance/confirm.png"):
                    self.logger.debug("REST STOP: EGO STATUS GIFT UPGRADED")
                    common.click_matching("pictures/mirror/restshop/enhance/confirm.png")

    def enhance_gifts(self,status):
        """Enhancement gift process"""
        for _ in range(3):
            common.sleep(1)
            if common.element_exist(status):
                shift_x, shift_y = mirror_utils.enhance_shift(self.status) or (12, -41)
                self.upgrade(status,shift_x,shift_y)

            if common.element_exist("pictures/mirror/restshop/enhance/wordless_enhance.png"):
                shift_x, shift_y = mirror_utils.enhance_shift("wordless")
                self.upgrade("pictures/mirror/restshop/enhance/wordless_enhance.png", shift_x, shift_y)

            if common.element_exist("pictures/mirror/restshop/scroll_bar.png"):
                common.click_matching("pictures/mirror/restshop/scroll_bar.png")
                for k in range(5):
                    common.mouse_scroll(-1000)  

    def event_choice(self):
        self.logger.info("Event")
        if common.element_exist("pictures/events/level_up.png"):
            self.logger.debug("Pass to Level Up")
            common.click_matching("pictures/events/level_up.png")
            common.click_matching("pictures/events/proceed.png")
            skill_check()

        if common.element_exist("pictures/events/select_gain.png"): #Select to gain EGO Gift
            self.logger.debug("Select to gain EGO Gift")
            common.click_matching("pictures/events/select_gain.png")
            #x,y = common.find_skip()
            #common.mouse_move_click(x,y)
            common.mouse_move_click(common.scale_x(1193),common.scale_y(623))
            while(True):
                common.mouse_click()
                if common.element_exist("pictures/events/proceed.png"):
                    common.click_matching("pictures/events/proceed.png")
                    break
                if common.element_exist("pictures/events/continue.png"):
                    common.click_matching("pictures/events/continue.png")
                    break
            common.sleep(1)
            if common.element_exist("pictures/mirror/general/ego_gift_get.png"): #handles the ego gift get
                common.click_matching("pictures/general/confirm_b.png")
                #common.key_press("enter")

        if common.element_exist("pictures/events/gain_check.png"): #Pass to gain an EGO Gift
            self.logger.debug("Pass to gain EGO Gift")
            common.click_matching("pictures/events/gain_check.png")
            common.wait_skip("pictures/events/proceed.png")
            skill_check()

        if common.element_exist("pictures/events/gain_gift.png"): #Proceed to gain
            self.logger.debug("Proceed to gain EGO Gift")
            common.click_matching("pictures/events/gain_gift.png")
            common.wait_skip("pictures/events/proceed.png")
            if common.element_exist("pictures/events/skip.png"):
                common.click_skip(4)
                self.event_choice()

        if common.element_exist("pictures/events/win_battle.png"): #Win battle to gain
            self.logger.debug("Win battle to gain EGO Gift")
            common.click_matching("pictures/events/win_battle.png")
            common.wait_skip("pictures/events/commence_battle.png")

        self.special_events()
        battle_check() #Just incase your pc has a very weird occurence of messing up

    def special_events(self):
        if common.element_exist("pictures/mirror/events/kqe.png"):
            self.logger.debug("KQE")
            common.click_matching("pictures/mirror/events/kqe.png")
            common.wait_skip("pictures/events/continue.png")
            if common.element_exist("pictures/mirror/general/ego_gift_get.png"): #handles the ego gift get
                common.click_matching("pictures/general/confirm_b.png")
                #common.key_press("enter") 

    def victory(self):
        self.logger.info("Run Won")
        if common.element_exist("pictures/general/confirm_w.png"):
            self.logger.debug("Manager Level Up")
            common.click_matching("pictures/general/confirm_w.png")
        common.click_matching("pictures/general/beeg_confirm.png")
        common.mouse_move(200,200)
        common.click_matching("pictures/general/claim_rewards.png")
        common.click_matching("pictures/general/md_claim.png")
        common.sleep(0.5)
        if common.element_exist("pictures/general/confirm_w.png"):
            self.logger.info("Rewards Claimed")
            common.click_matching("pictures/general/confirm_w.png")
            common.sleep(0.5)
            if common.element_exist("pictures/general/confirm_b.png"):
                self.logger.debug("BP PROMPT")
                common.click_matching("pictures/general/confirm_b.png")
                #common.key_press("enter")
            post_run_load()
        else: #incase not enough modules
            common.click_matching("pictures/general/to_window.png")
            common.click_matching("pictures/general/confirm_w.png")
            post_run_load()
            self.logger.info("You dont have enough modules to continue")
            exit() 

    def defeat(self):
        self.logger.info("Run Lost")
        if common.element_exist("pictures/general/confirm_w.png"):
            self.logger.debug("Manager Level Up")
            common.click_matching("pictures/general/confirm_w.png")
        common.click_matching("pictures/general/beeg_confirm.png")
        common.mouse_move(200,200)
        common.click_matching("pictures/general/claim_rewards.png")
        common.click_matching("pictures/general/give_up.png")
        common.click_matching("pictures/general/confirm_w.png")
        post_run_load()