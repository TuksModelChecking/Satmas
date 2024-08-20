import {
    Sheet,
    SheetClose,
    SheetContent,
    SheetDescription,
    SheetFooter,
    SheetHeader,
    SheetTitle,
    SheetTrigger,
} from "@/components/ui/sheet";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Settings as SettingsIcon } from "lucide-react";
import { useHotkeys } from "react-hotkeys-hook";
import { useState } from "react";

const Settings = () => {
    const [open, setOpen] = useState(false);
    useHotkeys("ctrl+b", () => { setOpen(!open) })

    return (
        <Sheet open={open} onOpenChange={() => setOpen(!open)}>
            <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="mt-auto rounded-lg" aria-label="Help">
                    <SettingsIcon />
                </Button>
            </SheetTrigger>
            <SheetContent>
                <SheetHeader>
                    <SheetTitle>Edit App Settings</SheetTitle>
                    <SheetDescription>
                        Make some configuration changes here. Click save when you're done.
                    </SheetDescription>
                </SheetHeader>
                <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4 mt-4">
                        <Label htmlFor="connectionString" className="text-left col-span-2">
                            SATMAS Solver Connection String
                        </Label>
                        <Input id="connectionString" value="localhost:50051" className="col-span-2" />
                    </div>
                </div>
                <SheetFooter>
                    <SheetClose asChild>
                        <div className="flex items-center mt-4 justify-start">
                            <Button className="mt-4" type="submit">Save changes</Button>
                        </div>
                    </SheetClose>
                </SheetFooter>
            </SheetContent>
        </Sheet>
    )
}

export default Settings;