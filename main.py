#coding:utf-8
import get_my_friends
import get_moods
import get_qq_number
import operate_table
import sys
import get_moods_detail

if __name__ == '__main__':

    #Create database
    operate_table_obj = operate_table.Operate_table()
    operate_table_obj.create_table()

    #If is given qq number, just run with
    #this qq number
    argv = sys.argv
    if len(argv) > 1:
        qq = argv[1]
        with open('qqnumber.inc', 'w') as qqfile:
            qqnumber_item = [{'data': qq, 'label': "Null"}]
            qqfile.write(str(qqnumber_item))

    else:
        # First, we need to get all our qq friends data
        get_friends_obj = get_my_friends.Get_friends_number()
        get_friends_obj.get_friends()

        # Second, deal with this data, clean it
        # From the get_friends result get the useful data
        # And save it to file qqnumber.inc
        # The format of this file just a list
        get_qq_item_obj = get_qq_number.exact_data_from_result()
        get_qq_item_obj.exact_qq_number()

    # Finally, use the cleaned data to get mood
    # Base on last step's qqnumber.inc file
    # exact the qq number and start to get their moods
    get_moods_obj = get_moods.Get_moods_start()
    get_moods_obj.get_moods_start()

