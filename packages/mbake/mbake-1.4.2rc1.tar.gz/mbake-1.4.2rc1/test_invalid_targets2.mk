# Invalid target with = sign
target=value: prerequisites
	recipe

# Invalid target with .RECIPEPREFIX character
.RECIPEPREFIX := >
>invalid: prerequisites
	recipe
