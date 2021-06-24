import sys
import sqlite3
import argparse


class DataBase:
    def __init__(self, db_name):
        try:
            self.db_name = db_name
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
        except:
            print("Error to connect DB!")
            return None

    def __str__(self):
        return f"Class DB {self.db_name}"

    def __repr__(self):
        return f"Class DB {self.db_name}"

    def do_commit(self):
        """do commit to DB"""
        self.conn.commit()

    def disconnect(self):
        """disconnect from DB"""
        self.conn.close()


class Table(DataBase):
    def __init__(self, table_name, db_name, *columns):
        super().__init__(db_name)
        self.table_name = table_name
        self.columns = columns
        self.columns_size = len(columns)
        self.last_row = 0

    def __str__(self):
        return f"This class Table; name_table is {self.table_name}"

    def __repr__(self):
        return f"This class Table; name_table is {self.table_name}"

    def excute_query(self, query):
        f"""Excute query for {self.table_name}"""
        try:
            self.cursor.execute(query)
            self.do_commit()
        except:
            print("Error to excute query!")

    def show_content(self):
        """Show content from the table"""
        try:
            line = f"SELECT * FROM {self.table_name}"
            result = self.cursor.execute(line).fetchall()
            for take1 in result:
                print(take1)
        except:
            print('Error show content from the table!')

    def take_content(self):
        """Return content from the table"""
        try:
            """Take content from the table"""
            line = f"SELECT * FROM {self.table_name}"
            result = self.cursor.execute(line).fetchall()
            return result
        except:
            print("Error to get content from table!")
            return None

    def insert_values(self, values):
        """Insert value to table"""
        try:
            line = "INSERT INTO {} VALUES ({},\'{}\')".format(self.table_name, self.last_row, '\',\''.join(values))
            self.last_row = self.cursor.execute(line).lastrowid
            self.do_commit()
            print(f'{values} insert to the table {self.table_name}')
        except:
            print("Error insert_value!")


def create_tables_1(db_name):
    meals = Table('meals', db_name, 'meal_id', 'meal_name')
    meals.excute_query(
        """
        CREATE TABLE IF NOT EXISTS meals(
        meal_id INT PRIMARY KEY,
        meal_name TEXT UNIQUE NOT NULL 
        )
        """
    )

    ingredients = Table('ingredients', db_name, 'ingredient_id', 'ingredient_name')
    ingredients.excute_query(
        """
        CREATE TABLE IF NOT EXISTS ingredients(
        ingredient_id INT PRIMARY KEY,
        ingredient_name TEXT UNIQUE NOT NULL
        )
        """
    )

    measures = Table('measures', db_name, 'measure_id', 'measure_name')
    measures.excute_query(
        """
        CREATE TABLE IF NOT EXISTS measures(
        measure_id INT PRIMARY KEY,
        measure_name UNIQUE
        )
        """
    )
    return meals, ingredients, measures


def insert_values_1(data, table):
    for value in data:
        table.insert_values([value])


def create_recipe(db_name):
    recipes = Table('recipes', db_name, 'recipe_id', 'recipe_name', 'recipe_description')
    recipes.excute_query(
        """
        CREATE TABLE recipes(
        recipe_id INT PRIMARY KEY,
        recipe_name TEXT NOT NULL,
        recipe_description TEXT
        )
        """
    )
    return recipes


def create_serve(db_name):
    serve = Table('serve', db_name, 'serve_id', 'recipe_id', 'meal_id')
    serve.excute_query(
        """
        CREATE TABLE serve(
        serve_id INT PRIMARY KEY,
        meal_id INT NOT NULL,
        recipe_id INT NOT NULL,
        FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id),
        FOREIGN KEY(meal_id) REFERENCES meals(meal_id)
        );
        """
    )
    return serve


def create_quantity(db_name):
    quantity = Table('quantity', db_name, 'quantity_id', 'measure_id', 'ingredient_id', 'quantity', 'recipe_id')
    quantity.excute_query(
        """
        CREATE TABLE quantity(
        quantity_id INT PRIMARY KEY,
        quantity INT NOT NULL,
        recipe_id INT NOT NULL,
        measure_id INT NOT NULL,
        ingredient_id INT NOT NULL,
        FOREIGN KEY (measure_id) REFERENCES measures(measure_id),
        FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id),
        FOREIGN KEY  (recipe_id) REFERENCES recipes(recipe_id)
        );
        """
    )
    return quantity


def main():
    parser = argparse.ArgumentParser(description="Food Blog Backend", epilog='DONE')
    parser.add_argument('dbname', help='dbname get', type=str)
    parser.add_argument('--ingredients',
                        help='Choose ingredients')
    parser.add_argument('--meals', help='meals')
    args = parser.parse_args()
    db_name = args.dbname
    user_ingredients = ''
    user_meals = ''

    if args.ingredients:
        user_ingredients = args.ingredients.split(',')
    if args.meals:
        user_meals = args.meals.split(',')


    if user_ingredients and user_meals:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        recipes_from_ing = set()
        recipes_from_mea = []
        set_flag_ing = False
        for ingredient in user_ingredients:
            ingredient_sets = ["milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"]
            if ingredient not in ingredient_sets:
                print("There are no such recipes in the database.")
                exit()
            ingredients_line = 'SELECT ingredients.ingredient_id FROM ingredients WHERE ingredients.ingredient_name= \'{}\''.format(ingredient)

            buff = cursor.execute(ingredients_line).fetchone()[0]
            ingredients_line = "SELECT quantity.recipe_id FROM quantity WHERE quantity.ingredient_id = {}".format(buff)
            if cursor.execute(ingredients_line).fetchall() is not None:
                buff = cursor.execute(ingredients_line).fetchall()
                ids = {buff[x][0] for x in range(len(buff))}
                if set_flag_ing is True:
                    recipes_from_ing = recipes_from_ing.intersection(ids)
                else:
                    recipes_from_ing = set(ids)
                    set_flag_ing = True
            conn.commit()

        set_flag_mea = False
        for meal in user_meals:
            meal_line = "SELECT meals.meal_id FROM meals WHERE meals.meal_name = '{}'".format(meal)
            buff = cursor.execute(meal_line).fetchone()[0]
            meal_line = "SELECT serve.recipe_id FROM serve WHERE serve.meal_id = {}".format(buff)
            if cursor.execute(meal_line).fetchall() is not None:
                buff = cursor.execute(meal_line).fetchall()
                ids = {buff[x][0] for x in range(len(buff))}
                if set_flag_mea is True:
                    recipes_from_mea = recipes_from_mea.intersection(ids)
                else:
                    recipes_from_mea = set(ids)

        recipes_set = recipes_from_ing.intersection(recipes_from_mea)
        recipes_set = tuple(recipes_set)
        if len(recipes_set) == 1:
            recipes_set = recipes_set[0]
            recipes_query = "SELECT recipes.recipe_name FROM recipes WHERE recipes.recipe_id = {}".format(recipes_set)
            recipes_names = cursor.execute(recipes_query).fetchone()[0]
            print(recipes_names)
            print("Recipes selected for you: " + recipes_names)

        else:
            recipes_query = "SELECT recipes.recipe_name FROM recipes WHERE recipes.recipe_id IN {}".format(recipes_set)
            recipes_names = cursor.execute(recipes_query).fetchall()
            recipes_names = [recipes_names[x][0] for x in range(len(recipes_names))]
            print("Recipes selected for you: " + ', '.join(recipes_names[::-1]))

    else:
        meals, ingredients, measures = create_tables_1(db_name)
        data = {
            "meals": ("breakfast", "brunch", "lunch", "supper"),
            "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
            "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")
        }
        insert_values_1(data['meals'], meals)
        insert_values_1(data['ingredients'], ingredients)
        insert_values_1(data['measures'], measures)

        recipes = create_recipe(db_name)
        serve = create_serve(db_name)
        quantity = create_quantity(db_name)

        measures_units = measures.take_content()
        measures_units = [measures_units[x][1] for x in range(len(measures_units))]
        ingredients_units = ingredients.take_content()
        ingredients_units = [ingredients_units[x][1] for x in range(len(ingredients_units))]

        print('Pass the empty recipe name to exit.')
        while True:
            quantity_flag = True
            recipe_name = input("Recipe name")
            if recipe_name:
                recipe_description = input("Recipe description")
                recipes.insert_values([recipe_name, recipe_description])
                print('1) breakfast  2) brunch  3) lunch  4) supper ')
                choices = input('When the dish can be served:')
                choices = choices.split(' ')
                for i in choices:
                    serve.insert_values([str(int(i) - 1), str(recipes.last_row - 1)])
                while quantity_flag:
                    quantity_line = input("Input quantity of ingredient <press enter to stop>:")
                    if quantity_line:
                        quantity_line = quantity_line.split(' ')
                        if len(quantity_line) == 3:
                            if quantity_line[1] in measures_units and quantity_line[2] in ingredients_units:
                                quantity.insert_values([quantity_line[0], str(recipes.last_row - 1),
                                                        str(measures_units.index(quantity_line[1])),
                                                        str(ingredients_units.index(quantity_line[2]))])
                            elif quantity_line[1] in measures_units:
                                quantity_line[2] = 'blackberry'
                                quantity.insert_values([quantity_line[0], str(recipes.last_row - 1),
                                                        str(measures_units.index(quantity_line[1])),
                                                        str(ingredients_units.index(quantity_line[2]))])
                                print('The ingredient is not conclusive!')
                            else:
                                print('The measure is not conclusive!')
                        else:
                            quantity_line.insert(1, '')
                            if quantity_line[1] in measures_units and quantity_line[2] in ingredients_units:
                                quantity.insert_values([quantity_line[0], str(recipes.last_row - 1),
                                                        str(measures_units.index(quantity_line[1])),
                                                        str(ingredients_units.index(quantity_line[2]))])
                            elif quantity_line[1] in measures_units:
                                print('The ingredient is not conclusive!')
                            else:
                                print('The measure is not conclusive!')
                    else:
                        quantity_flag = False
            else:
                break
        pass


if __name__ == '__main__':
    main()
